import pytest
from license_scanner.cli import main
from unittest.mock import patch


@patch("main.tomllib.load")
def test_good_weather(toml_load_mock):
    toml_load_mock.return_value = {
        "tool": {"license_scanner": {"allowed_licenses": [], "allowed_packages": []}}
    }
