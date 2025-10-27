# %%
from typing import Dict, List

from .parse_license import parse_license
from .parse_license.licenses_synonyms import unknown_license
from .get_all_packages import get_all_package_names

import importlib.metadata as im


def get_licenses(name: str) -> List[str]:
    """Get the licenses for a given package.
    This will return the raw license strings, which can be parsed with parse_license.
    Only "UNKNOWN" in the licenses field will be skipped.

    :param name: The name of the package
    :type name: str
    :return: A list of licenses for the package
    :rtype: List[str]
    """
    all_licenses = []
    try:
        metas = im.metadata(name)
    except im.PackageNotFoundError:
        return [unknown_license]
    for key, value in metas.items():
        if key == "License-Expression":
            license = value
            if license:
                all_licenses.append(license)
        if key == "License":
            license = value
            if license == "UNKNOWN":
                # Sometimes this is unknown because it is not filled in
                continue
            if license:
                all_licenses.append(license)
        if key == "Classifier":
            if not value.startswith("License ::"):
                continue
            license = value.split("::")[-1]
            if license.strip() == "OSI Approved":
                continue
            if license:
                all_licenses.append(license)

    all_licenses = all_licenses
    return all_licenses


def get_all_licenses() -> Dict[str, str]:
    """
    Get all packages installed in the environment and their licenses.
    This will return a dictionary with the license as key and a list of packages names as value.

    :return: A dictionary with the license as key and a list of packages names as value
    :rtype: Dict[str, str]
    """
    all_licenses = {}
    all_package_names = get_all_package_names()

    for package_name in all_package_names:
        licenses_raw = get_licenses(package_name)

        # Parse and remove duplicates
        licenses = list(set([parse_license(i) for i in licenses_raw]))
        licenses = [i for i in licenses if i]

        # If no license is known let it know
        if len(licenses) == 0:
            licenses = [unknown_license]

        # Reformat output
        for _license in licenses:
            all_licenses[_license] = all_licenses.get(_license, []) + [package_name]

    return all_licenses
