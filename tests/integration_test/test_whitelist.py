from unittest.mock import patch

import pytest
from src.license_scanner.cli import main


@pytest.mark.parametrize(
    "allowed_licenses, allowed_packages",
    [
        (
            [
                "BSD license",
                "MiT",
                "Apache-2.0",
                "Historical Permission Notice and Disclaimer (HPND)",
                "CMU License (MIT-CMU)",
            ],
            [],
        ),
        (
            [
                "BSD license",
                "Apache-2.0",
                "Historical Permission Notice and Disclaimer (HPND)",
                "CMU License (MIT-CMU)",
            ],
            ["mergedeep", "jaraco.text"],
        ),
        (
            [
                "BSD license",
                "MiT",
                "Apache-2.0",
            ],
            ["pillow"],
        ),
        (
            [
                "BSD license",
                "MiT",
                "Historical Permission Notice and Disclaimer (HPND)",
                "CMU License (MIT-CMU)",
            ],
            ["absl_py"],
        ),
    ],
    ids=[
        "pure allowed licenses",
        "no MIT",
        "no HPND or MIT-CMU",
        "no Apache 2.0",
    ],
)
@patch("src.license_scanner.cli.tomllib.load")
def test_whitelist_integration_passing(
    toml_load_mock,
    allowed_licenses,
    allowed_packages,
):
    toml_load_mock.return_value = {
        "tool": {
            "license_scanner": {
                "allowed_licenses": allowed_licenses,
                "allowed_packages": allowed_packages,
            }
        }
    }
    main()
