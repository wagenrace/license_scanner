# %%
from typing import Dict, List

from .parse_license import parse_license
from .parse_license.licenses_synonyms import unknown_license
from .get_all_packages import get_all_package_names

import importlib.metadata as im


def get_license(name: str) -> List[str]:
    all_licenses = []
    try:
        metas = im.metadata(name)
    except im.PackageNotFoundError:
        return [unknown_license]
    for key, value in metas.items():
        if key == "License-Expression":
            license = value
            if license:
                all_licenses.append(parse_license(license))
        if key == "License":
            license = value
            if license == "UNKNOWN":
                # Sometimes this is unknown because it is not filled in
                continue
            if license:
                all_licenses.append(parse_license(license))
        if key == "Classifier":
            if not value.startswith("License ::"):
                continue
            license = value.split("::")[-1]
            if license.strip() == "OSI Approved":
                continue
            if license:
                all_licenses.append(parse_license(license))

    all_licenses = list(set(all_licenses))
    return all_licenses


def get_all_licenses() -> Dict[str, str]:
    all_licenses = {}
    all_package_names = get_all_package_names()

    for package_name in all_package_names:
        licenses = get_license(package_name)

        for license in licenses:
            all_licenses[license] = all_licenses.get(license, []) + [package_name]

    return all_licenses
