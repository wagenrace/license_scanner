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


import functools
import importlib
import importlib.machinery
import os
import re
import types
import warnings
import zipfile
from collections.abc import Iterable
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Literal,
    TypeVar,
    Union,
    overload,
)

# workaround for #4476
sys.modules.pop("backports", None)

if TYPE_CHECKING:
    from _typeshed import BytesPath, StrOrBytesPath, StrPath
    from _typeshed.importlib import LoaderProtocol
    from typing_extensions import TypeAlias

warnings.warn(
    "pkg_resources is deprecated as an API. "
    "See https://setuptools.pypa.io/en/latest/pkg_resources.html",
    DeprecationWarning,
    stacklevel=2,
)

# Type aliases
# Any object works, but let's indicate we expect something like a module (optionally has __loader__ or __file__)
_ModuleLike: TypeAlias = Union[object, types.ModuleType]
# Any: Should be _ModuleLike but we end up with issues where _ModuleLike doesn't have _ZipLoaderModule's __loader__
_ProviderFactoryType: TypeAlias = Callable[[Any], "IResourceProvider"]


class PEP440Warning(RuntimeWarning):
    """
    Used when there is an issue with a version or specifier not complying with
    PEP 440.
    """


class ResolutionError(Exception):
    """Abstract base for dependency resolution errors"""

    def __repr__(self) -> str:
        return self.__class__.__name__ + repr(self.args)


class UnknownExtra(ResolutionError):
    """Distribution doesn't have an "extra feature" of the given name"""


_provider_factories: dict[type[_ModuleLike], _ProviderFactoryType] = {}


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


class DefaultProvider:
    """Provides access to package resources in the filesystem"""

    egg_info: str | None = None
    loader: LoaderProtocol | None = None

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


def find_distributions(path_item: str, only: bool = False) -> Iterable[Distribution]:
    """Yield distributions accessible via `path_item`"""
    return find_on_path(path_item, only)


def find_on_path(path_item, only=False):
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
    if not os.path.isdir(path):
        return ()
    return os.listdir(path)


def distributions_from_metadata(path: str):
    if os.path.isdir(path):
        if len(os.listdir(path)) == 0:
            # empty metadata dir; skip
            return

    entry = os.path.basename(path)
    yield Distribution.from_location(
        entry,
    )


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


class Distribution:
    """Wrap an actual or potential sys.path entry w/metadata"""

    PKG_INFO = "PKG-INFO"

    def __init__(
        self,
        project_name: str | None = None,
        platform: str | None = None,
    ) -> None:
        self.project_name = safe_name(project_name or "Unknown")
        self.platform = platform

    @classmethod
    def from_location(
        cls,
        basename: StrPath,
        **kw: int,  # We could set `precedence` explicitly, but keeping this as `**kw` for full backwards and subclassing compatibility
    ) -> Distribution:
        project_name, platform = [None] * 2
        basename, _ = os.path.splitext(basename)

        match = EGG_NAME(basename)
        if match:
            project_name, platform = match.group("name", "plat")
        return cls(
            project_name=project_name,
            platform=platform,
            **kw,
        )


# Silence the PEP440Warning by default, so that end users don't get hit by it
# randomly just because they use pkg_resources. We want to append the rule
# because we want earlier uses of filterwarnings to take precedence over this
# one.
warnings.filterwarnings("ignore", category=PEP440Warning, append=True)


if __name__ == "__main__":
    # This part of the code should keep on working
    # coverage run copy_pkg_resources.py; coverage report; coverage html
    entries = sys.path

    all_package_names = []
    for entry in entries:
        dists = find_on_path(entry)
        if dists:
            for dist in dists:
                all_package_names.append(dist.project_name)
    print(f"All package names {len(all_package_names)}:", sorted(all_package_names))
    print(f"Are there unknowns: {'Unknown' in all_package_names}")
