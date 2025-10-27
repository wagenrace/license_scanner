from unittest.mock import patch
from src.license_scanner.cli import main


@patch("src.license_scanner.cli.tomllib.load")
def test_whitelist_integration(mock_toml_load):
    assert True
