import os

from .licenses_synonyms import LICENSES_SYNONYMS, unknown_license

current_loc = os.path.dirname(os.path.realpath(__file__))


def parse_license(license_str: str):
    # Get license
    if not license_str:
        return None
    license_str = license_str.strip()

    if "copyright (c) " in license_str:
        license_str = license_str.lower().split("copyright (c) ")[0]

    if len(license_str) > 300:
        license_str = license_str[:300]

    license_str = license_str if license_str else unknown_license
    license_str = LICENSES_SYNONYMS.get(license_str.lower())
    return license_str
