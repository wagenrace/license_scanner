from unittest.mock import patch

import pytest

from src.license_scanner.cli import Mode, main


@pytest.mark.parametrize(
    "allowed_licenses, allowed_packages, all_licenses",
    [
        (["BSD license"], [], {"MIT license": ["package-1", "package-2"]}),
        ([], ["package-1"], {"BSD license": ["package-1", "package-2"]}),
        (
            ["MIT license"],
            ["package-4"],
            {"MIT license": ["package-1", "package-2"], "BSD license": ["package-3"]},
        ),
    ],
    ids=[
        "not allowed licenses",
        "not allowed packages",
        "not allowed licenses and packages",
    ],
)
@patch("src.license_scanner.cli.__get_arguments")
@patch("src.license_scanner.cli.get_all_licenses")
@patch("src.license_scanner.cli.tomllib.load")
def test_white_listed_licenses_fail(
    toml_load_mock,
    get_all_licenses_mock,
    argparse_mock,
    allowed_licenses,
    allowed_packages,
    all_licenses,
):
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


@pytest.mark.parametrize(
    "allowed_licenses, allowed_packages, all_licenses",
    [
        (["BSD license"], [], {"BSD license": ["package_1", "package-2"]}),
        ([], ["package-1", "package_2"], {"BSD license": ["package_1", "package-2"]}),
        (
            ["MIT license"],
            ["package-3"],
            {"MIT license": ["package-1", "package-2"], "BSD license": ["package-3"]},
        ),
        (
            ["MIT", "BSD", "apache 2.0"],
            [],
            {
                "MIT license": ["package-1"],
                "BSD license": ["package-2"],
                "Apache license 2.0": ["package-3"],
            },
        ),
        (
            [
                'BSD 4-Clause "Original" or "Old" License',
                'BSD 3-Clause "New" or "Revised" License',
                "GNU Affero General Public License v1.0 or later",
                "Historical Permission Notice and Disclaimer (HPND)",
                "FSF Unlimited License (With License Retention and Warranty Disclaimer)",
            ],
            [],
            {
                'BSD 4-Clause "Original" or "Old" License': ["package-1"],
                'BSD 3-Clause "New" or "Revised" License': ["package-2"],
                "GNU Affero General Public License v1.0 or later": ["package-3"],
                "Historical Permission Notice and Disclaimer (HPND)": ["package-4"],
                "FSF Unlimited License (With License Retention and Warranty Disclaimer)": [
                    "package-5"
                ],
            },
        ),
    ],
    ids=[
        "allowed licenses",
        "allowed packages",
        "allowed licenses and packages",
        "synonyms",
        "licenses with OR/AND it in the name",
    ],
)
@patch("src.license_scanner.cli.__get_arguments")
@patch("src.license_scanner.cli.get_all_licenses")
@patch("src.license_scanner.cli.tomllib.load")
def test_white_listed_licenses(
    toml_load_mock,
    get_all_licenses_mock,
    argparse_mock,
    allowed_licenses,
    allowed_packages,
    all_licenses,
):
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
