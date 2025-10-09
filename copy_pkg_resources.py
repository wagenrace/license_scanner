"""
Package resource API
--------------------

A resource is a logical file contained within a package, or a logical
subdirectory thereof.  The package resource API expects resource names
to have their path parts separated with ``/``, *not* whatever the local
path separator is.  Do not use os.path operations to manipulate resource
names being passed into the API.

The package resource API is designed to work with normal filesystem packages,
.egg files, and unpacked .egg files.  It can also work in a limited way with
.zip files and with custom PEP 302 loaders that support the ``get_data()``
method.

This module is deprecated. Users are directed to :mod:`importlib.resources`,
:mod:`importlib.metadata` and :pypi:`packaging` instead.
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 9):  # noqa: UP036 # Check for unsupported versions
    raise RuntimeError("Python 3.9 or later is required")

import _imp
import collections
import email.parser
import errno
import functools
import importlib
import importlib.abc
import importlib.machinery
import inspect
import io
import ntpath
import operator
import os
import pkgutil
import platform
import plistlib
import posixpath
import re
import stat
import tempfile
import textwrap
import time
import types
import warnings
import zipfile
import zipimport
from collections.abc import Iterable, Iterator, Mapping, MutableSequence
from pkgutil import get_importer
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Callable,
    Literal,
    NamedTuple,
    NoReturn,
    Protocol,
    TypeVar,
    Union,
    overload,
)

# workaround for #4476
sys.modules.pop("backports", None)

# capture these to bypass sandboxing
from os import open as os_open, utime  # isort: skip
from os.path import isdir, split  # isort: skip

try:
    from os import mkdir, rename, unlink

    WRITE_SUPPORT = True
except ImportError:
    # no write support, probably under GAE
    WRITE_SUPPORT = False

import packaging.markers
import packaging.requirements
import packaging.specifiers
import packaging.utils
import packaging.version
from jaraco.text import drop_comment, join_continuation, yield_lines
from platformdirs import user_cache_dir as _user_cache_dir

if TYPE_CHECKING:
    from _typeshed import BytesPath, StrOrBytesPath, StrPath
    from _typeshed.importlib import LoaderProtocol
    from typing_extensions import Self, TypeAlias

warnings.warn(
    "pkg_resources is deprecated as an API. "
    "See https://setuptools.pypa.io/en/latest/pkg_resources.html",
    DeprecationWarning,
    stacklevel=2,
)

_T = TypeVar("_T")
_DistributionT = TypeVar("_DistributionT", bound="Distribution")
# Type aliases
_NestedStr: TypeAlias = Union[str, Iterable[Union[str, Iterable["_NestedStr"]]]]
_StrictInstallerType: TypeAlias = Callable[["Requirement"], "_DistributionT"]
_InstallerType: TypeAlias = Callable[["Requirement"], Union["Distribution", None]]
_PkgReqType: TypeAlias = Union[str, "Requirement"]
_EPDistType: TypeAlias = Union["Distribution", _PkgReqType]
_MetadataType: TypeAlias = Union["IResourceProvider", None]
_ResolvedEntryPoint: TypeAlias = Any  # Can be any attribute in the module
_ResourceStream: TypeAlias = Any  # TODO / Incomplete: A readable file-like object
# Any object works, but let's indicate we expect something like a module (optionally has __loader__ or __file__)
_ModuleLike: TypeAlias = Union[object, types.ModuleType]
# Any: Should be _ModuleLike but we end up with issues where _ModuleLike doesn't have _ZipLoaderModule's __loader__
_ProviderFactoryType: TypeAlias = Callable[[Any], "IResourceProvider"]
_DistFinderType: TypeAlias = Callable[[_T, str, bool], Iterable["Distribution"]]
_NSHandlerType: TypeAlias = Callable[[_T, str, str, types.ModuleType], Union[str, None]]
_AdapterT = TypeVar(
    "_AdapterT", _DistFinderType[Any], _ProviderFactoryType, _NSHandlerType[Any]
)


_PEP440_FALLBACK = re.compile(r"^v?(?P<safe>(?:[0-9]+!)?[0-9]+(?:\.[0-9]+)*)", re.I)


class PEP440Warning(RuntimeWarning):
    """
    Used when there is an issue with a version or specifier not complying with
    PEP 440.
    """


parse_version = packaging.version.Version

_state_vars: dict[str, str] = {}


def _declare_state(vartype: str, varname: str, initial_value: _T) -> _T:
    _state_vars[varname] = vartype
    return initial_value


class ResolutionError(Exception):
    """Abstract base for dependency resolution errors"""

    def __repr__(self) -> str:
        return self.__class__.__name__ + repr(self.args)


class VersionConflict(ResolutionError):
    """
    An already-installed version conflicts with the requested version.

    Should be initialized with the installed Distribution and the requested
    Requirement.
    """

    _template = "{self.dist} is installed but {self.req} is required"

    @property
    def dist(self) -> Distribution:
        return self.args[0]

    @property
    def req(self) -> Requirement:
        return self.args[1]

    def report(self):
        return self._template.format(**locals())

    def with_context(
        self, required_by: set[Distribution | str]
    ) -> Self | ContextualVersionConflict:
        """
        If required_by is non-empty, return a version of self that is a
        ContextualVersionConflict.
        """
        if not required_by:
            return self
        args = self.args + (required_by,)
        return ContextualVersionConflict(*args)


class ContextualVersionConflict(VersionConflict):
    """
    A VersionConflict that accepts a third parameter, the set of the
    requirements that required the installed Distribution.
    """

    _template = VersionConflict._template + " by {self.required_by}"

    @property
    def required_by(self) -> set[str]:
        return self.args[2]


class DistributionNotFound(ResolutionError):
    """A requested distribution was not found"""

    _template = (
        "The '{self.req}' distribution was not found "
        "and is required by {self.requirers_str}"
    )

    @property
    def req(self) -> Requirement:
        return self.args[0]

    @property
    def requirers(self) -> set[str] | None:
        return self.args[1]

    @property
    def requirers_str(self):
        if not self.requirers:
            return "the application"
        return ", ".join(self.requirers)

    def report(self):
        return self._template.format(**locals())

    def __str__(self) -> str:
        return self.report()


class UnknownExtra(ResolutionError):
    """Distribution doesn't have an "extra feature" of the given name"""


_provider_factories: dict[type[_ModuleLike], _ProviderFactoryType] = {}

PY_MAJOR = f"{sys.version_info.major}.{sys.version_info.minor}"
EGG_DIST = 3
BINARY_DIST = 2
SOURCE_DIST = 1
CHECKOUT_DIST = 0
DEVELOP_DIST = -1


def register_loader_type(
    loader_type: type[_ModuleLike], provider_factory: _ProviderFactoryType
) -> None:
    """Register `provider_factory` to make providers for `loader_type`

    `loader_type` is the type or class of a PEP 302 ``module.__loader__``,
    and `provider_factory` is a function that, passed a *module* object,
    returns an ``IResourceProvider`` for that module.
    """
    _provider_factories[loader_type] = provider_factory


def safe_name(name: str) -> str:
    """Convert an arbitrary string to a standard distribution name

    Any runs of non-alphanumeric/. characters are replaced with a single '-'.
    """
    return re.sub("[^A-Za-z0-9.]+", "-", name)


def safe_version(version: str) -> str:
    """
    Convert an arbitrary string to a standard version string
    """
    try:
        # normalize the version
        return str(packaging.version.Version(version))
    except packaging.version.InvalidVersion:
        version = version.replace(" ", ".")
        return re.sub("[^A-Za-z0-9.]+", "-", version)


def safe_extra(extra: str) -> str:
    """Convert an arbitrary string to a standard 'extra' name

    Any runs of non-alphanumeric characters are replaced with a single '_',
    and the result is always lowercased.
    """
    return re.sub("[^A-Za-z0-9.-]+", "_", extra).lower()


def to_filename(name: str) -> str:
    """Convert a project or version name to its filename-escaped form

    Any '-' characters are currently replaced with '_'.
    """
    return name.replace("-", "_")


def invalid_marker(text: str) -> SyntaxError | Literal[False]:
    """
    Validate text as a PEP 508 environment marker; return an exception
    if invalid or False otherwise.
    """
    try:
        evaluate_marker(text)
    except SyntaxError as e:
        e.filename = None
        e.lineno = None
        return e
    return False


def evaluate_marker(text: str, extra: str | None = None) -> bool:
    """
    Evaluate a PEP 508 environment marker.
    Return a boolean indicating the marker result in this environment.
    Raise SyntaxError if marker is invalid.

    This implementation uses the 'pyparsing' module.
    """
    try:
        marker = packaging.markers.Marker(text)
        return marker.evaluate()
    except packaging.markers.InvalidMarker as e:
        raise SyntaxError(e) from e


class NullProvider:
    """Try to implement resources and metadata for arbitrary PEP 302 loaders"""

    egg_name: str | None = None
    egg_info: str | None = None
    loader: LoaderProtocol | None = None

    def __init__(self, module: _ModuleLike) -> None:
        pass

    def _get_metadata_path(self, name):
        return self._fn(self.egg_info, name)

    def has_metadata(self, name: str) -> bool:
        if not self.egg_info:
            return False

        path = self._get_metadata_path(name)
        return self._has(path)

    def get_metadata(self, name: str) -> str:
        if not self.egg_info:
            return ""
        path = self._get_metadata_path(name)
        value = self._get(path)
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError as exc:
            # Include the path in the error message to simplify
            # troubleshooting, and without changing the exception type.
            exc.reason += f" in {name} file at path: {path}"
            raise

    def get_metadata_lines(self, name: str) -> Iterator[str]:
        return yield_lines(self.get_metadata(name))

    def resource_isdir(self, resource_name: str) -> bool:
        return self._isdir(self._fn(self.module_path, resource_name))

    def _fn(self, base: str | None, resource_name: str):
        if base is None:
            raise TypeError(
                "`base` parameter in `_fn` is `None`. Either override this method or check the parameter first."
            )
        self._validate_resource_path(resource_name)
        if resource_name:
            return os.path.join(base, *resource_name.split("/"))
        return base

    @staticmethod
    def _validate_resource_path(path) -> None:
        """
        Validate the resource paths according to the docs.
        https://setuptools.pypa.io/en/latest/pkg_resources.html#basic-resource-access

        >>> warned = getfixture('recwarn')
        >>> warnings.simplefilter('always')
        >>> vrp = NullProvider._validate_resource_path
        >>> vrp('foo/bar.txt')
        >>> bool(warned)
        False
        >>> vrp('../foo/bar.txt')
        >>> bool(warned)
        True
        >>> warned.clear()
        >>> vrp('/foo/bar.txt')
        >>> bool(warned)
        True
        >>> vrp('foo/../../bar.txt')
        >>> bool(warned)
        True
        >>> warned.clear()
        >>> vrp('foo/f../bar.txt')
        >>> bool(warned)
        False

        Windows path separators are straight-up disallowed.
        >>> vrp(r'\\foo/bar.txt')
        Traceback (most recent call last):
        ...
        ValueError: Use of .. or absolute path in a resource path \
is not allowed.

        >>> vrp(r'C:\\foo/bar.txt')
        Traceback (most recent call last):
        ...
        ValueError: Use of .. or absolute path in a resource path \
is not allowed.

        Blank values are allowed

        >>> vrp('')
        >>> bool(warned)
        False

        Non-string values are not.

        >>> vrp(None)
        Traceback (most recent call last):
        ...
        AttributeError: ...
        """
        invalid = (
            os.path.pardir in path.split(posixpath.sep)
            or posixpath.isabs(path)
            or ntpath.isabs(path)
            or path.startswith("\\")
        )
        if not invalid:
            return

        msg = "Use of .. or absolute path in a resource path is not allowed."

        # Aggressively disallow Windows absolute paths
        if (path.startswith("\\") or ntpath.isabs(path)) and not posixpath.isabs(path):
            raise ValueError(msg)

        # for compatibility, warn; in future
        # raise ValueError(msg)
        issue_warning(
            msg[:-1] + " and will raise exceptions in a future release.",
            DeprecationWarning,
        )

    def _get(self, path) -> bytes:
        if hasattr(self.loader, "get_data") and self.loader:
            # Already checked get_data exists
            return self.loader.get_data(path)  # type: ignore[attr-defined]
        raise NotImplementedError(
            "Can't perform this operation for loaders without 'get_data()'"
        )


register_loader_type(object, NullProvider)


def _parents(path):
    """
    yield all parents of path including path
    """
    last = None
    while path != last:
        yield path
        last = path
        path, _ = os.path.split(path)


class EggProvider(NullProvider):
    """Provider based on a virtual filesystem"""

    def __init__(self, module: _ModuleLike) -> None:
        super().__init__(module)
        self._setup_prefix()

    def _setup_prefix(self):
        # Assume that metadata may be nested inside a "basket"
        # of multiple eggs and use module_path instead of .archive.
        eggs = filter(_is_egg_path, _parents(self.module_path))
        egg = next(eggs, None)
        egg and self._set_egg(egg)

    def _set_egg(self, path: str) -> None:
        self.egg_name = os.path.basename(path)
        self.egg_info = os.path.join(path, "EGG-INFO")
        self.egg_root = path


class DefaultProvider(EggProvider):
    """Provides access to package resources in the filesystem"""

    def _has(self, path) -> bool:
        return os.path.exists(path)

    def _isdir(self, path) -> bool:
        return os.path.isdir(path)

    def _listdir(self, path):
        return os.listdir(path)

    def get_resource_stream(
        self, manager: object, resource_name: str
    ) -> io.BufferedReader:
        return open(self._fn(self.module_path, resource_name), "rb")

    def _get(self, path) -> bytes:
        with open(path, "rb") as stream:
            return stream.read()

    @classmethod
    def _register(cls) -> None:
        loader_names = (
            "SourceFileLoader",
            "SourcelessFileLoader",
        )
        for name in loader_names:
            loader_cls = getattr(importlib.machinery, name, type(None))
            register_loader_type(loader_cls, cls)


DefaultProvider._register()


class EmptyProvider:
    """Provider that returns nothing for all requests"""

    # A special case, we don't want all Providers inheriting from NullProvider to have a potentially None module_path
    module_path: str | None = None  # type: ignore[assignment]

    _isdir = _has = lambda self, path: False

    def _get(self, path) -> bytes:
        return b""

    def _listdir(self, path):
        return []

    def __init__(self) -> None:
        pass


empty_provider = EmptyProvider()


class ZipManifests(dict[str, "MemoizedZipManifests.manifest_mod"]):
    """
    zip manifest builder
    """

    # `path` could be `StrPath | IO[bytes]` but that violates the LSP for `MemoizedZipManifests.load`
    @classmethod
    def build(cls, path: str) -> dict[str, zipfile.ZipInfo]:
        """
        Build a dictionary similar to the zipimport directory
        caches, except instead of tuples, store ZipInfo objects.

        Use a platform-specific path separator (os.sep) for the path keys
        for compatibility with pypy on Windows.
        """
        with zipfile.ZipFile(path) as zfile:
            items = (
                (
                    name.replace("/", os.sep),
                    zfile.getinfo(name),
                )
                for name in zfile.namelist()
            )
            return dict(items)

    load = build


class MemoizedZipManifests(ZipManifests):
    """
    Memoized zipfile manifests.
    """

    class manifest_mod(NamedTuple):
        manifest: dict[str, zipfile.ZipInfo]
        mtime: float


class FileMetadata(EmptyProvider):
    """Metadata handler for standalone PKG-INFO files

    Usage::

        metadata = FileMetadata("/path/to/PKG-INFO")

    This provider rejects all data and metadata requests except for PKG-INFO,
    which is treated as existing, and will be the contents of the file at
    the provided location.
    """

    def __init__(self, path: StrPath) -> None:
        self.path = path

    def _get_metadata_path(self, name):
        return self.path

    def has_metadata(self, name: str) -> bool:
        return name == "PKG-INFO" and os.path.isfile(self.path)

    def get_metadata(self, name: str) -> str:
        if name != "PKG-INFO":
            raise KeyError("No metadata except PKG-INFO is available")

        with open(self.path, encoding="utf-8", errors="replace") as f:
            metadata = f.read()
        self._warn_on_replacement(metadata)
        return metadata

    def _warn_on_replacement(self, metadata) -> None:
        replacement_char = "�"
        if replacement_char in metadata:
            tmpl = "{self.path} could not be properly decoded in UTF-8"
            msg = tmpl.format(**locals())
            warnings.warn(msg)

    def get_metadata_lines(self, name: str) -> Iterator[str]:
        return yield_lines(self.get_metadata(name))


class PathMetadata(DefaultProvider):
    """Metadata provider for egg directories

    Usage::

        # Development eggs:

        egg_info = "/path/to/PackageName.egg-info"
        base_dir = os.path.dirname(egg_info)
        metadata = PathMetadata(base_dir, egg_info)
        dist_name = os.path.splitext(os.path.basename(egg_info))[0]
        dist = Distribution(basedir, project_name=dist_name, metadata=metadata)

        # Unpacked egg directories:

        egg_path = "/path/to/PackageName-ver-pyver-etc.egg"
        metadata = PathMetadata(egg_path, os.path.join(egg_path,'EGG-INFO'))
        dist = Distribution.from_filename(egg_path, metadata=metadata)
    """

    def __init__(self, path: str, egg_info: str) -> None:
        self.module_path = path
        self.egg_info = egg_info


_distribution_finders: dict[type, _DistFinderType[Any]] = _declare_state(
    "dict", "_distribution_finders", {}
)


def register_finder(
    importer_type: type[_T], distribution_finder: _DistFinderType[_T]
) -> None:
    """Register `distribution_finder` to find distributions in sys.path items

    `importer_type` is the type or class of a PEP 302 "Importer" (sys.path item
    handler), and `distribution_finder` is a callable that, passed a path
    item and the importer instance, yields ``Distribution`` instances found on
    that path item.  See ``pkg_resources.find_on_path`` for an example."""
    _distribution_finders[importer_type] = distribution_finder


def find_distributions(path_item: str, only: bool = False) -> Iterable[Distribution]:
    """Yield distributions accessible via `path_item`"""
    importer = get_importer(path_item)
    finder = _find_adapter(_distribution_finders, importer)
    return finder(importer, path_item, only)


def find_nothing(
    importer: object | None, path_item: str | None, only: bool | None = False
):
    return ()


register_finder(object, find_nothing)


def find_on_path(importer: object | None, path_item, only=False):
    """Yield distributions accessible on a sys.path directory"""
    path_item = _normalize_cached(path_item)

    if _is_unpacked_egg(path_item):
        yield Distribution.from_filename(
            path_item,
            metadata=PathMetadata(path_item, os.path.join(path_item, "EGG-INFO")),
        )
        return

    entries = (os.path.join(path_item, child) for child in safe_listdir(path_item))

    # scan for .egg and .egg-info in directory
    for entry in sorted(entries):
        fullpath = os.path.join(path_item, entry)
        factory = dist_factory(path_item, entry, only)
        yield from factory(fullpath)


def dist_factory(path_item, entry, only):
    """Return a dist_factory for the given entry."""
    lower = entry.lower()
    is_egg_info = lower.endswith(".egg-info")
    is_dist_info = lower.endswith(".dist-info") and os.path.isdir(
        os.path.join(path_item, entry)
    )
    is_meta = is_egg_info or is_dist_info
    return (
        distributions_from_metadata
        if is_meta
        else (
            find_distributions
            if not only and _is_egg_path(entry)
            else (
                resolve_egg_link
                if not only and lower.endswith(".egg-link")
                else NoDists()
            )
        )
    )


class NoDists:
    """
    >>> bool(NoDists())
    False

    >>> list(NoDists()('anything'))
    []
    """

    def __bool__(self) -> Literal[False]:
        return False

    def __call__(self, fullpath: object):
        return iter(())


def safe_listdir(path: StrOrBytesPath):
    """
    Attempt to list contents of path, but suppress some exceptions.
    """
    try:
        return os.listdir(path)
    except (PermissionError, NotADirectoryError):
        pass
    except OSError as e:
        # Ignore the directory if does not exist, not a directory or
        # permission denied
        if e.errno not in (errno.ENOTDIR, errno.EACCES, errno.ENOENT):
            raise
    return ()


def distributions_from_metadata(path: str):
    root = os.path.dirname(path)
    if os.path.isdir(path):
        if len(os.listdir(path)) == 0:
            # empty metadata dir; skip
            return
        metadata: _MetadataType = PathMetadata(root, path)
    else:
        metadata = FileMetadata(path)
    entry = os.path.basename(path)
    yield Distribution.from_location(
        root,
        entry,
        metadata,
        precedence=DEVELOP_DIST,
    )


def non_empty_lines(path):
    """
    Yield non-empty lines from file at path
    """
    for line in _read_utf8_with_fallback(path).splitlines():
        line = line.strip()
        if line:
            yield line


def resolve_egg_link(path):
    """
    Given a path to an .egg-link, resolve distributions
    present in the referenced path.
    """
    referenced_paths = non_empty_lines(path)
    resolved_paths = (
        os.path.join(os.path.dirname(path), ref) for ref in referenced_paths
    )
    dist_groups = map(find_distributions, resolved_paths)
    return next(dist_groups, ())


if hasattr(pkgutil, "ImpImporter"):
    register_finder(pkgutil.ImpImporter, find_on_path)

register_finder(importlib.machinery.FileFinder, find_on_path)

_namespace_handlers: dict[type, _NSHandlerType[Any]] = _declare_state(
    "dict", "_namespace_handlers", {}
)
_namespace_packages: dict[str | None, list[str]] = _declare_state(
    "dict", "_namespace_packages", {}
)


def register_namespace_handler(
    importer_type: type[_T], namespace_handler: _NSHandlerType[_T]
) -> None:
    """Register `namespace_handler` to declare namespace packages

    `importer_type` is the type or class of a PEP 302 "Importer" (sys.path item
    handler), and `namespace_handler` is a callable like this::

        def namespace_handler(importer, path_entry, moduleName, module):
            # return a path_entry to use for child packages

    Namespace handlers are only called if the importer object has already
    agreed that it can handle the relevant path item, and they should only
    return a subpath if the module __path__ does not already contain an
    equivalent subpath.  For an example namespace handler, see
    ``pkg_resources.file_ns_handler``.
    """
    _namespace_handlers[importer_type] = namespace_handler


def _handle_ns(packageName, path_item):
    """Ensure that named package includes a subpath of path_item (if needed)"""

    importer = get_importer(path_item)
    if importer is None:
        return None

    # use find_spec (PEP 451) and fall-back to find_module (PEP 302)
    try:
        spec = importer.find_spec(packageName)
    except AttributeError:
        # capture warnings due to #1111
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            loader = importer.find_module(packageName)
    else:
        loader = spec.loader if spec else None

    if loader is None:
        return None
    module = sys.modules.get(packageName)
    if module is None:
        module = sys.modules[packageName] = types.ModuleType(packageName)
        module.__path__ = []
        _set_parent_ns(packageName)
    elif not hasattr(module, "__path__"):
        raise TypeError("Not a package:", packageName)
    handler = _find_adapter(_namespace_handlers, importer)
    subpath = handler(importer, path_item, packageName, module)
    if subpath is not None:
        path = module.__path__
        path.append(subpath)
        importlib.import_module(packageName)
        _rebuild_mod_path(path, packageName, module)
    return subpath


def _rebuild_mod_path(orig_path, package_name, module: types.ModuleType) -> None:
    """
    Rebuild module.__path__ ensuring that all entries are ordered
    corresponding to their sys.path order
    """
    sys_path = [_normalize_cached(p) for p in sys.path]

    def safe_sys_path_index(entry):
        """
        Workaround for #520 and #513.
        """
        try:
            return sys_path.index(entry)
        except ValueError:
            return float("inf")

    def position_in_sys_path(path):
        """
        Return the ordinal of the path based on its position in sys.path
        """
        path_parts = path.split(os.sep)
        module_parts = package_name.count(".") + 1
        parts = path_parts[:-module_parts]
        return safe_sys_path_index(_normalize_cached(os.sep.join(parts)))

    new_path = sorted(orig_path, key=position_in_sys_path)
    new_path = [_normalize_cached(p) for p in new_path]

    if isinstance(module.__path__, list):
        module.__path__[:] = new_path
    else:
        module.__path__ = new_path


def declare_namespace(packageName: str) -> None:
    """Declare that package 'packageName' is a namespace package"""

    msg = (
        f"Deprecated call to `pkg_resources.declare_namespace({packageName!r})`.\n"
        "Implementing implicit namespace packages (as specified in PEP 420) "
        "is preferred to `pkg_resources.declare_namespace`. "
        "See https://setuptools.pypa.io/en/latest/references/"
        "keywords.html#keyword-namespace-packages"
    )
    warnings.warn(msg, DeprecationWarning, stacklevel=2)

    _imp.acquire_lock()
    try:
        if packageName in _namespace_packages:
            return

        path: MutableSequence[str] = sys.path
        parent, _, _ = packageName.rpartition(".")

        if parent:
            declare_namespace(parent)
            if parent not in _namespace_packages:
                __import__(parent)
            try:
                path = sys.modules[parent].__path__
            except AttributeError as e:
                raise TypeError("Not a package:", parent) from e

        # Track what packages are namespaces, so when new path items are added,
        # they can be updated
        _namespace_packages.setdefault(parent or None, []).append(packageName)
        _namespace_packages.setdefault(packageName, [])

        for path_item in path:
            # Ensure all the parent's path items are reflected in the child,
            # if they apply
            _handle_ns(packageName, path_item)

    finally:
        _imp.release_lock()


def fixup_namespace_packages(path_item: str, parent: str | None = None) -> None:
    """Ensure that previously-declared namespace packages include path_item"""
    _imp.acquire_lock()
    try:
        for package in _namespace_packages.get(parent, ()):
            subpath = _handle_ns(package, path_item)
            if subpath:
                fixup_namespace_packages(subpath, package)
    finally:
        _imp.release_lock()


def file_ns_handler(
    importer: object,
    path_item: StrPath,
    packageName: str,
    module: types.ModuleType,
):
    """Compute an ns-package subpath for a filesystem or zipfile importer"""

    subpath = os.path.join(path_item, packageName.split(".")[-1])
    normalized = _normalize_cached(subpath)
    for item in module.__path__:
        if _normalize_cached(item) == normalized:
            break
    else:
        # Only return the path if it's not already there
        return subpath


if hasattr(pkgutil, "ImpImporter"):
    register_namespace_handler(pkgutil.ImpImporter, file_ns_handler)

register_namespace_handler(zipimport.zipimporter, file_ns_handler)
register_namespace_handler(importlib.machinery.FileFinder, file_ns_handler)


def null_ns_handler(
    importer: object,
    path_item: str | None,
    packageName: str | None,
    module: _ModuleLike | None,
) -> None:
    return None


register_namespace_handler(object, null_ns_handler)


@overload
def normalize_path(filename: StrPath) -> str: ...
@overload
def normalize_path(filename: BytesPath) -> bytes: ...
def normalize_path(filename: StrOrBytesPath) -> str | bytes:
    """Normalize a file/dir name for comparison purposes"""
    return os.path.normcase(os.path.realpath(os.path.normpath(_cygwin_patch(filename))))


def _cygwin_patch(filename: StrOrBytesPath):  # pragma: nocover
    """
    Contrary to POSIX 2008, on Cygwin, getcwd (3) contains
    symlink components. Using
    os.path.abspath() works around this limitation. A fix in os.getcwd()
    would probably better, in Cygwin even more so, except
    that this seems to be by design...
    """
    return os.path.abspath(filename) if sys.platform == "cygwin" else filename


if TYPE_CHECKING:
    # https://github.com/python/mypy/issues/16261
    # https://github.com/python/typeshed/issues/6347
    @overload
    def _normalize_cached(filename: StrPath) -> str: ...
    @overload
    def _normalize_cached(filename: BytesPath) -> bytes: ...
    def _normalize_cached(filename: StrOrBytesPath) -> str | bytes: ...

else:

    @functools.cache
    def _normalize_cached(filename):
        return normalize_path(filename)


def _is_egg_path(path):
    """
    Determine if given path appears to be an egg.
    """
    return _is_zip_egg(path) or _is_unpacked_egg(path)


def _is_zip_egg(path):
    return (
        path.lower().endswith(".egg")
        and os.path.isfile(path)
        and zipfile.is_zipfile(path)
    )


def _is_unpacked_egg(path):
    """
    Determine if given path appears to be an unpacked egg.
    """
    return path.lower().endswith(".egg") and os.path.isfile(
        os.path.join(path, "EGG-INFO", "PKG-INFO")
    )


def _set_parent_ns(packageName) -> None:
    parts = packageName.split(".")
    name = parts.pop()
    if parts:
        parent = ".".join(parts)
        setattr(sys.modules[parent], name, sys.modules[packageName])


MODULE = re.compile(r"\w+(\.\w+)*$").match
EGG_NAME = re.compile(
    r"""
    (?P<name>[^-]+) (
        -(?P<ver>[^-]+) (
            -py(?P<pyver>[^-]+) (
                -(?P<plat>.+)
            )?
        )?
    )?
    """,
    re.VERBOSE | re.IGNORECASE,
).match


def _version_from_file(lines):
    """
    Given an iterable of lines from a Metadata file, return
    the value of the Version field, if present, or None otherwise.
    """

    def is_version_line(line):
        return line.lower().startswith("version:")

    version_lines = filter(is_version_line, lines)
    line = next(iter(version_lines), "")
    _, _, value = line.partition(":")
    return safe_version(value.strip()) or None


class Distribution:
    """Wrap an actual or potential sys.path entry w/metadata"""

    PKG_INFO = "PKG-INFO"

    def __init__(
        self,
        location: str | None = None,
        metadata: _MetadataType = None,
        project_name: str | None = None,
        version: str | None = None,
        py_version: str | None = PY_MAJOR,
        platform: str | None = None,
        precedence: int = EGG_DIST,
    ) -> None:
        self.project_name = safe_name(project_name or "Unknown")
        if version is not None:
            self._version = safe_version(version)
        self.py_version = py_version
        self.platform = platform
        self.location = location
        self.precedence = precedence
        self._provider = metadata or empty_provider

    @classmethod
    def from_location(
        cls,
        location: str,
        basename: StrPath,
        metadata: _MetadataType = None,
        **kw: int,  # We could set `precedence` explicitly, but keeping this as `**kw` for full backwards and subclassing compatibility
    ) -> Distribution:
        project_name, version, py_version, platform = [None] * 4
        basename, ext = os.path.splitext(basename)
        if ext.lower() in _distributionImpl:
            cls = _distributionImpl[ext.lower()]

            match = EGG_NAME(basename)
            if match:
                project_name, version, py_version, platform = match.group(
                    "name", "ver", "pyver", "plat"
                )
        return cls(
            location,
            metadata,
            project_name=project_name,
            version=version,
            py_version=py_version,
            platform=platform,
            **kw,
        )._reload_version()

    def _reload_version(self):
        return self

    def _get_metadata(self, name):
        if self.has_metadata(name):
            yield from self.get_metadata_lines(name)

    def _get_version(self):
        lines = self._get_metadata(self.PKG_INFO)
        return _version_from_file(lines)

    def __getattr__(self, attr: str):
        """Delegate all unrecognized public attributes to .metadata provider"""
        if attr.startswith("_"):
            raise AttributeError(attr)
        return getattr(self._provider, attr)


class EggInfoDistribution(Distribution):
    def _reload_version(self):
        """
        Packages installed by distutils (e.g. numpy or scipy),
        which uses an old safe_version, and so
        their version numbers can get mangled when
        converted to filenames (e.g., 1.11.0.dev0+2329eae to
        1.11.0.dev0_2329eae). These distributions will not be
        parsed properly
        downstream by Distribution and safe_version, so
        take an extra step and try to get the version number from
        the metadata file itself instead of the filename.
        """
        md_version = self._get_version()
        if md_version:
            self._version = md_version
        return self


class DistInfoDistribution(Distribution):
    """
    Wrap an actual or potential sys.path entry
    w/metadata, .dist-info style.
    """

    PKG_INFO = "METADATA"
    EQEQ = re.compile(r"([\(,])\s*(\d.*?)\s*([,\)])")


_distributionImpl = {
    ".egg": Distribution,
    ".egg-info": EggInfoDistribution,
    ".dist-info": DistInfoDistribution,
}


def _always_object(classes):
    """
    Ensure object appears in the mro even
    for old-style classes.
    """
    if object not in classes:
        return classes + (object,)
    return classes


def _find_adapter(registry: Mapping[type, _AdapterT], ob: object) -> _AdapterT:
    """Return an adapter factory for `ob` from `registry`"""
    types = _always_object(inspect.getmro(getattr(ob, "__class__", type(ob))))
    for t in types:
        if t in registry:
            return registry[t]
    # _find_adapter would previously return None, and immediately be called.
    # So we're raising a TypeError to keep backward compatibility if anyone depended on that behaviour.
    raise TypeError(f"Could not find adapter for {registry} and {ob}")


# Silence the PEP440Warning by default, so that end users don't get hit by it
# randomly just because they use pkg_resources. We want to append the rule
# because we want earlier uses of filterwarnings to take precedence over this
# one.
warnings.filterwarnings("ignore", category=PEP440Warning, append=True)


class PkgResourcesDeprecationWarning(Warning):
    """
    Base class for warning about deprecations in ``pkg_resources``

    This class is not derived from ``DeprecationWarning``, and as such is
    visible by default.
    """


# Ported from ``setuptools`` to avoid introducing an import inter-dependency:
_LOCALE_ENCODING = "locale" if sys.version_info >= (3, 10) else None


# This must go before calls to `_call_aside`. See https://github.com/pypa/setuptools/pull/4422
def _read_utf8_with_fallback(file: str, fallback_encoding=_LOCALE_ENCODING) -> str:
    """See setuptools.unicode_utils._read_utf8_with_fallback"""
    try:
        with open(file, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:  # pragma: no cover
        msg = f"""\
        ********************************************************************************
        `encoding="utf-8"` fails with {file!r}, trying `encoding={fallback_encoding!r}`.

        This fallback behaviour is considered **deprecated** and future versions of
        `setuptools/pkg_resources` may not implement it.

        Please encode {file!r} with "utf-8" to ensure future builds will succeed.

        If this file was produced by `setuptools` itself, cleaning up the cached files
        and re-building/re-installing the package with a newer version of `setuptools`
        (e.g. by updating `build-system.requires` in its `pyproject.toml`)
        might solve the problem.
        ********************************************************************************
        """
        # TODO: Add a deadline?
        #       See comment in setuptools.unicode_utils._Utf8EncodingNeeded
        warnings.warn(msg, PkgResourcesDeprecationWarning, stacklevel=2)
        with open(file, "r", encoding=fallback_encoding) as f:
            return f.read()


if __name__ == "__main__":
    # This part of the code should keep on working
    # coverage run copy_pkg_resources.py
    # coverage report
    # coverage html
    entries = sys.path

    all_package_names = []
    for entry in entries:
        dists = find_distributions(entry)
        if dists:
            for dist in dists:
                all_package_names.append(dist.project_name)
    print(f"All package names {len(all_package_names)}:", sorted(all_package_names))
