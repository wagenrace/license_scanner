from unittest.mock import patch

import pytest

from license_scanner.cli import Mode, main


@patch("license_scanner.cli.__get_arguments")
@patch("license_scanner.cli.get_all_licenses")
@patch("license_scanner.cli.tomllib.load")
def test_nothing_allowed(toml_load_mock, get_all_licenses_mock, argparse_mock):
    toml_load_mock.return_value = {
        "tool": {"license_scanner": {"allowed_licenses": [], "allowed_packages": []}}
    }
    get_all_licenses_mock.return_value = {"BSD license": ["package 1", "package 2"]}
    argparse_mock.return_value = Mode.whitelist

    with pytest.raises(ValueError):
        main()


@patch("license_scanner.cli.__get_arguments")
@patch("license_scanner.cli.get_all_licenses")
@patch("license_scanner.cli.tomllib.load")
def test_white_listed_licenses(toml_load_mock, get_all_licenses_mock, argparse_mock):
    toml_load_mock.return_value = {
        "tool": {
            "license_scanner": {
                "allowed_licenses": ["BSD license"],
                "allowed_packages": [],
            }
        }
    }
    get_all_licenses_mock.return_value = {"BSD license": ["package 1", "package 2"]}
    argparse_mock.return_value = Mode.whitelist

    main()


@patch("license_scanner.cli.__get_arguments")
@patch("license_scanner.cli.get_all_licenses")
@patch("license_scanner.cli.tomllib.load")
def test_white_listed_packages(toml_load_mock, get_all_licenses_mock, argparse_mock):
    toml_load_mock.return_value = {
        "tool": {
            "license_scanner": {
                "allowed_licenses": [],
                "allowed_packages": ["package 1", "package 2"],
            }
        }
    }
    get_all_licenses_mock.return_value = {"BSD license": ["package 1", "package 2"]}
    argparse_mock.return_value = Mode.whitelist

    main()


@patch("license_scanner.cli.__get_arguments")
@patch("license_scanner.cli.get_all_licenses")
@patch("license_scanner.cli.tomllib.load")
def test_white_listed_license_and_packages(
    toml_load_mock, get_all_licenses_mock, argparse_mock
):
    toml_load_mock.return_value = {
        "tool": {
            "license_scanner": {
                "allowed_licenses": ["BSD license"],
                "allowed_packages": ["package 3"],
            }
        }
    }
    get_all_licenses_mock.return_value = {
        "BSD license": ["package 1", "package 2"],
        "MIT license": ["package 3"],
    }
    argparse_mock.return_value = Mode.whitelist

    main()
