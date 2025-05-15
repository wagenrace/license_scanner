from pandas import read_html
import requests
from license_scanner.parse_license import parse_license

license_url = "https://spdx.org/licenses/"


def get_spdx_licenses() -> list[str]:
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

    # Extract the license IDs and names
    _licenses += license_table["Full name"].to_list()
    _licenses += license_table["Identifier"].to_list()

    # Second table contains Deprecated License Identifiers
    license_table_depracted = tables[1]

    # Extract the license IDs and names
    _licenses += license_table_depracted["Full name"].to_list()
    _licenses += license_table_depracted["Identifier"].to_list()

    return _licenses


licenses = get_spdx_licenses()
number_of_not_found = 0
for l in licenses:
    license_parsed = parse_license(l)
    if license_parsed is None:
        number_of_not_found += 1
        print(
            f'{str(number_of_not_found).zfill(4)}: "{l.lower()}" not found in license_scanner'
        )

if number_of_not_found == 0:
    print("All licenses found in license_scanner")
else:
    print(f"{number_of_not_found} licenses not found in license_scanner")
    exit(1)
