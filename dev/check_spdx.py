import pandas as pd
from typing import List
from pandas import read_html
import requests
from license_scanner.parse_license import parse_license
from license_scanner.parse_license.licenses_synonyms import LICENSES_SYNONYMS

license_url = "https://spdx.org/licenses/"


def get_spdx_licenses() -> List[List[str]]:
    """
    Get all SPDX licenses from the SPDX website.
    """
    # Get the HTML content of the page
    response = requests.get(license_url)
    html_content = response.content

    # Parse the HTML content using pandas
    tables = read_html(html_content, flavor="bs4")

    _licenses = []
    # First table contains the license data
    license_table = tables[0]

    # Second table contains Deprecated License Identifiers
    license_table_depracted = tables[1]

    full_table = pd.concat(
        [
            license_table[["Full name", "Identifier"]],
            license_table_depracted[["Full name", "Identifier"]],
        ]
    )
    # Extract the license IDs and names
    for row in full_table.iterrows():
        license_name = row[1]["Full name"]
        license_id = row[1]["Identifier"]
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
