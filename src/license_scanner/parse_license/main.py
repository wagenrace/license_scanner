import os

from .licenses_synonyms import LICENSES_SYNONYMS, unknown_license

current_loc = os.path.dirname(os.path.realpath(__file__))


def remove_trailing_whitespace(string: str):
    if string.endswith((" ", "\t", "\n", "\r")):
        return remove_trailing_whitespace(string[:-1])
    return string


def parse_license(license_str: str):
    # Get license
    if not license_str:
        return None
    license_str = remove_trailing_whitespace(license_str)

    if "copyright (c) " in license_str:
        license_str = license_str.lower().split("copyright (c) ")[0]

    if len(license_str) > 300:
        license_str = license_str[:300]

    license_str = license_str if license_str else unknown_license
    license_str = LICENSES_SYNONYMS.get(license_str.lower())
    return license_str
