import os
import warnings
from typing import Union
from .licenses_synonyms import LICENSES_SYNONYMS, unknown_license

current_loc = os.path.dirname(os.path.realpath(__file__))


def parse_license(license_str: str) -> Union[str, None]:
    """Turn a general license name into one of that is in the list
    This makes it easier to compare license that might be differently written.

    If the license string seems to be a full license, None is returned.
    If the license is not found in the list of known licenses, a warning is raised
    and the original string is returned.

    :param license_str: license string found in package metadata
    :type license_str: str
    :return: normalized license string
    :rtype: str | None
    """
    # Get license
    if not license_str:
        return None

    # If a break line is in there, it is a whole license.
    # Don't bother
    if "\n" in license_str:
        # Only print the first 5 lines
        part_of_license = repr("\n".join(license_str.split("\n")[:5]))
        warnings.warn(
            f"It seems like a full license (not just a name) was paste for license: {part_of_license}"
        )
        return None

    # Make case insensitive
    license_str = license_str.lower()

    if "copyright (c) " in license_str:
        license_str = license_str.split("copyright (c) ")[0]

    if len(license_str) > 300:
        license_str = license_str[:300]

    # Strip whitespace, this is done last to not interfere with full license check
    license_str = license_str.strip()

    license_normalized = LICENSES_SYNONYMS.get(license_str)
    if license_normalized is None:
        warnings.warn(
            f'The license "{license_str}" was not found in list of known licenses'
        )
        license_normalized = license_str

    # Replace empty with unknown
    license_normalized = license_normalized if license_normalized else unknown_license
    return license_normalized
