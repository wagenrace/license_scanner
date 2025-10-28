from unittest.mock import patch

import pytest
from src.license_scanner.cli import main, Mode

PYTEST_PACKAGES = [
    "colorama",
    "exceptiongroup",
    "iniconfig",
    "packaging",
    "pluggy",
    "pygments",
    "pytest",
    "tomli",
    "typing_extensions",
    "autocommand",
]


@pytest.mark.parametrize(
    "allowed_licenses, allowed_packages",
    [
        (
            [
                "BSD license",
                "BSD 2-clause license",
                "BSD 3-clause license",
                "MiT",
                "Apache-2.0",
                "Apache license",
                "Historical Permission Notice and Disclaimer (HPND)",
                "CMU License (MIT-CMU)",
            ],
            [*PYTEST_PACKAGES],
        ),
        (
            [
                "BSD license",
                "BSD 2-clause license",
                "BSD 3-clause license",
                "MiT",
                "Apache license",
                "Apache-2.0",
            ],
            ["pillow", *PYTEST_PACKAGES],
        ),
        (
            [
                "BSD license",
                "BSD 2-clause license",
                "BSD 3-clause license",
                "Apache license",
                "MiT",
                "Historical Permission Notice and Disclaimer (HPND)",
                "CMU License (MIT-CMU)",
            ],
            ["absl_py", *PYTEST_PACKAGES],
        ),
        (
            [
                "BSD license",
                "BSD 2-clause license",
                "BSD 3-clause license",
                "Apache license",
                "MiT",
                "Historical Permission Notice and Disclaimer (HPND)",
                "CMU License (MIT-CMU)",
            ],
            ["absl-py", *PYTEST_PACKAGES],
        ),
    ],
    ids=[
        "pure allowed licenses",
        "no HPND or MIT-CMU",
        "no Apache 2.0",
        "no Apache 2.0 used - in package name",
    ],
)
@patch("src.license_scanner.cli.__get_arguments")
@patch("src.license_scanner.cli.tomllib.load")
def test_whitelist_integration_passing(
    toml_load_mock,
    argparse_mock,
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
    argparse_mock.return_value = Mode.whitelist
    main()


@pytest.mark.parametrize(
    "allowed_licenses, allowed_packages",
    [
        (
            [
                "BSD license",
                "BSD 2-clause license",
                "BSD 3-clause license",
                "Apache-2.0",
                "Apache license",
                "Historical Permission Notice and Disclaimer (HPND)",
                "CMU License (MIT-CMU)",
            ],
            [*PYTEST_PACKAGES],
        ),
        (
            [
                "BSD license",
                "BSD 2-clause license",
                "BSD 3-clause license",
                "MiT",
                "Apache license",
                "Apache-2.0",
            ],
            [*PYTEST_PACKAGES],
        ),
        (
            [
                "BSD license",
                "BSD 2-clause license",
                "BSD 3-clause license",
                "Apache license",
                "MiT",
                "Historical Permission Notice and Disclaimer (HPND)",
                "CMU License (MIT-CMU)",
            ],
            [*PYTEST_PACKAGES],
        ),
    ],
    ids=[
        "no MIT",
        "no HPND or MIT-CMU",
        "no Apache 2.0",
    ],
)
@patch("src.license_scanner.cli.__get_arguments")
@patch("src.license_scanner.cli.tomllib.load")
def test_whitelist_integration_failing(
    toml_load_mock,
    argparse_mock,
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
    argparse_mock.return_value = Mode.whitelist
    with pytest.raises(ValueError):
        main()
