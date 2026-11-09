from typing import List
import requests
from license_scanner.parse_license import parse_license
from license_scanner.parse_license.licenses_synonyms import LICENSES_SYNONYMS

license_url = "https://raw.githubusercontent.com/spdx/license-list-data/refs/heads/main/json/licenses.json"


def get_spdx_licenses() -> List[List[str]]:
    """
    Get all SPDX licenses from the SPDX website.
    """
    # Get the JSON content of the page
    response = requests.get(license_url)
    json_content = response.json()

    _licenses = []
    for license in json_content["licenses"]:
        license_name = license["name"]
        license_id = license["licenseId"]
        license_parsed = parse_license(license_name)
        license_id_parsed = parse_license(license_id)
        if (
            LICENSES_SYNONYMS.get(license_parsed.lower()) is None
            or LICENSES_SYNONYMS.get(license_id_parsed.lower()) is None
        ):
            _licenses.append([license_name, license_id])
    return _licenses


def create_variable_name(license_id: str) -> str:
    """
    Create a variable name from the license ID.
    """
    variable_name = license_id.lower().replace("-", "_").replace(".", "_")
    if variable_name[0].isdigit():
        variable_name = "_" + variable_name
    return variable_name


licenses = get_spdx_licenses()

if len(licenses) == 0:
    print("All licenses found in license_scanner")
else:
    print(f"{len(licenses)} licenses not found in license_scanner")
    # Print for readme
    print("\nREADME\n")
    for _license in licenses:
        print(f"- {_license[0]}")
    # Print new variables
    print("\nVariables\n")

    for _license in licenses:
        variable_name = create_variable_name(_license[1])
        print(f'{variable_name} = "{_license[0]}"')
    print("\nSynonyms\n")
    # Print first lines of LICENSES_SYNONYMS
    for _license in licenses:
        variable_name = create_variable_name(_license[1])
        print(f"{variable_name}.lower() : {variable_name},")
    print("\nIDs\n")
    # add ids
    for _license in licenses:
        variable_name = create_variable_name(_license[1])
        print(f'"{_license[1].lower()}" : {variable_name},')
    exit(1)
