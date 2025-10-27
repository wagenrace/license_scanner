from unittest.mock import patch

import pytest

from src.license_scanner.parse_license import parse_license
from src.license_scanner.cli import Mode, main
from src.license_scanner.parse_license.licenses_synonyms import LICENSES_SYNONYMS

ALL_KNOWN_LICENSES = list(LICENSES_SYNONYMS.keys())
ALL_ALLOWED_LICENSES = list(set(LICENSES_SYNONYMS.values()))


@pytest.mark.parametrize(
    "license_name",
    ALL_KNOWN_LICENSES,
)
@patch("src.license_scanner.cli.__get_arguments")
@patch("src.license_scanner.cli.get_all_licenses")
@patch("src.license_scanner.cli.tomllib.load")
def test_all_licenses_positive(
    toml_load_mock,
    get_all_licenses_mock,
    argparse_mock,
    license_name,
):
    """
    Test for EVERY license synonym known if it would create a positive hit
    """
    allowed_licenses = [license_name]
    allowed_packages = []
    all_licenses = {license_name: ["package 1", "package 2"]}

    toml_load_mock.return_value = {
        "tool": {
            "license_scanner": {
                "allowed_licenses": allowed_licenses,
                "allowed_packages": allowed_packages,
            }
        }
    }
    get_all_licenses_mock.return_value = all_licenses
    argparse_mock.return_value = Mode.whitelist

    main()


@pytest.mark.parametrize(
    "license_name",
    ALL_KNOWN_LICENSES,
)
@patch("src.license_scanner.cli.__get_arguments")
@patch("src.license_scanner.cli.get_all_licenses")
@patch("src.license_scanner.cli.tomllib.load")
def test_all_licenses_negative(
    toml_load_mock,
    get_all_licenses_mock,
    argparse_mock,
    license_name,
):
    """
    Test for EVERY license synonym known if it would create a negative hit
    """
    allowed_licenses = ALL_ALLOWED_LICENSES.copy()
    allowed_licenses.remove(parse_license(license_name))
    allowed_packages = []
    all_licenses = {license_name: ["package 1", "package 2"]}

    toml_load_mock.return_value = {
        "tool": {
            "license_scanner": {
                "allowed_licenses": allowed_licenses,
                "allowed_packages": allowed_packages,
            }
        }
    }
    get_all_licenses_mock.return_value = all_licenses
    argparse_mock.return_value = Mode.whitelist

    with pytest.raises(ValueError):
        main()
