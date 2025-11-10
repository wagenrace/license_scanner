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
    "setuptools",
]


@pytest.mark.parametrize(
    "allowed_licenses, allowed_packages",
    [
        (
            [
                "BSD license",
                "BSD 2-clause license",
                "BSD 3-clause license",
                "GNU Lesser General Public License v2.0",
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
                "GNU Lesser GenEral Public License v2.0",
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
                "LGPL-2.0-only",
                "Apache license",
                "GNU Lesser GenEral Public License v2.0",
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
                "lgpl-2.0-only",
                "Apache license",
                "GNU Lesser GenEral Public License v2.0",
                "MiT",
                "Historical Permission Notice and Disclaimer (HPND)",
                "CMU License (MIT-CMU)",
            ],
            ["absl-py", *PYTEST_PACKAGES],
        ),
        (
            [
                "BSD license",
                "BSD 2-clause license",
                "BSD 3-clause license",
                "lgpl-2.0-only",
                "Apache license",
                "Apache-2.0",
                "MiT",
                "Historical Permission Notice and Disclaimer (HPND)",
                "CMU License (MIT-CMU)",
            ],
            ["pycdlib", *PYTEST_PACKAGES],
        ),
    ],
    ids=[
        "pure allowed licenses",
        "no HPND or MIT-CMU",
        "no Apache 2.0",
        "no Apache 2.0 used - in package name",
        "No LGPL-2.0-only used - in package name",
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
                "GNU Lesser GenEral Public License v2.0",
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
                "GNU Lesser GenEral Public License v2.0",
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
                "GNU Lesser GenEral Public License v2.0",
                "Apache license",
                "MiT",
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
                "Apache-2.0",
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
        "No LGPL-2.0-only",
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
