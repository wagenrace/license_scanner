import os
import warnings
from .licenses_synonyms import LICENSES_SYNONYMS, unknown_license

current_loc = os.path.dirname(os.path.realpath(__file__))


def parse_license(license_str: str):
    # Get license
    if not license_str:
        return None

    # If a break line is in there, it is a whole license.
    # Don't bother
    if "\n" in license_str:
        warnings.warn(
            f"It seems like a full license (not just a name) was paste for license: {repr(license_str)}"
        )
        return None

    license_str = license_str.strip()

    if "copyright (c) " in license_str:
        license_str = license_str.lower().split("copyright (c) ")[0]

    if len(license_str) > 300:
        license_str = license_str[:300]

    license_str = license_str if license_str else unknown_license
    license_normalized = LICENSES_SYNONYMS.get(license_str.lower())
    if license_normalized is None:
        warnings.warn(
            f'The license "{license_str}" was not found in list of known licenses'
        )
        license_normalized = license_str

    return license_normalized
