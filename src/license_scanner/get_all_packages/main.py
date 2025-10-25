from __future__ import annotations

import sys

import os
import re
from typing import List


def safe_listdir(path):
    """
    Attempt to list contents of path, but suppress some exceptions.
    """
    if not os.path.isdir(path):
        return ()
    return os.listdir(path)


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


def get_package_name(basename) -> str:
    match = EGG_NAME(basename)
    if match:
        project_name = match.group("name")
        return project_name
    return None


def _cygwin_patch(filename):  # pragma: nocover
    """
    Contrary to POSIX 2008, on Cygwin, getcwd (3) contains
    symlink components. Using
    os.path.abspath() works around this limitation. A fix in os.getcwd()
    would probably better, in Cygwin even more so, except
    that this seems to be by design...
    """
    return os.path.abspath(filename) if sys.platform == "cygwin" else filename


def normalize_path(filename) -> str | bytes:
    """Normalize a file/dir name for comparison purposes"""
    return os.path.normcase(os.path.realpath(os.path.normpath(_cygwin_patch(filename))))


def get_all_package_names() -> List[str]:
    """Get all package names installed into the environment

    :return: list of package names
    :rtype: List[str]
    """
    all_package_names = []

    for sys_path in sys.path:
        sys_path = normalize_path(sys_path)
        all_modules = safe_listdir(sys_path)
        for module_folder_name in all_modules:
            lower = str(module_folder_name).lower()
            is_egg_info = lower.endswith(".egg-info")
            if is_egg_info:
                package_name = module_folder_name[: -len(".egg-info")]
            is_dist_info = lower.endswith(".dist-info") and os.path.isdir(
                os.path.join(sys_path, module_folder_name)
            )
            if is_dist_info:
                package_name = module_folder_name[: -len(".dist-info")]

            if is_egg_info or is_dist_info:
                package_name: str = get_package_name(package_name)
                if package_name:
                    all_package_names.append(package_name)
                else:
                    print(f"Could not parse package name from {module_folder_name}")
                    all_package_names.append(module_folder_name)

    return all_package_names


if __name__ == "__main__":
    all_package_names = get_all_package_names()

    print(f"All package names {len(all_package_names)}:", sorted(all_package_names))
    print(f"Are there unknowns: {'Unknown' in all_package_names}")
