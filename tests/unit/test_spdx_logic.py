import pytest
from src.license_scanner.spdx_logic.main import spdx_logic


def test_spdx_single_license_no_MIT():
    allowed_licenses = [
        "Apache-2.0",
        "BSD-3-Clause",
        "completely unknown license",
    ]

    assert spdx_logic("MIT", allowed_licenses) is False


def test_spdx_single_license_MIT():
    allowed_licenses = [
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "completely unknown license",
    ]
    assert spdx_logic("MIT", allowed_licenses) is True


def test_spdx_single_license_Apache_2_0():
    allowed_licenses = [
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "completely unknown license",
    ]
    assert spdx_logic("Apache-2.0", allowed_licenses) is True


def test_spdx_single_license_BSD_3_Clause():
    allowed_licenses = [
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "completely unknown license",
    ]
    assert spdx_logic("BSD-3-Clause", allowed_licenses) is True


def test_spdx_single_license_GPL_3_0():
    allowed_licenses = [
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "completely unknown license",
    ]
    assert spdx_logic("GPL-3.0", allowed_licenses) is False

    # License NOT named in SPDX, but present in allowed licenses


def test_spdx_single_license_MIT_license():
    allowed_licenses = [
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "completely unknown license",
    ]
    assert spdx_logic("MIT license", allowed_licenses) is True


def test_spdx_single_license_BSD_3_Clause_license():
    allowed_licenses = [
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "completely unknown license",
    ]
    assert spdx_logic("BSD 3-clause license", allowed_licenses) is True


def test_spdx_single_license_GPL_version_3():
    allowed_licenses = [
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "completely unknown license",
    ]
    assert spdx_logic("GPL version 3", allowed_licenses) is False


def test_spdx_single_license_mit_0():
    allowed_licenses = [
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "completely unknown license",
    ]
    assert spdx_logic("mit 0", allowed_licenses) is False

    # License NOT named in SPDX and NOT present in allowed licenses


def test_spdx_single_license_completely_unknown_license():
    allowed_licenses = [
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "completely unknown license",
    ]
    assert spdx_logic("completely unknown license", allowed_licenses) is True


def test_spdx_single_license_another_unknown_license():
    allowed_licenses = [
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "completely unknown license",
    ]
    assert spdx_logic("another unknown license", allowed_licenses) is False


def test_spdx_simple_expressions_or_both_allowed():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]

    assert spdx_logic("MIT OR Apache-2.0", allowed_licenses) is True


def test_spdx_simple_expressions_or_one_allowed():
    allowed_licenses = ["MIT", "BSD-3-Clause"]
    assert spdx_logic("MIT OR GPL-3.0", allowed_licenses) is True


def test_spdx_simple_expressions_or_other_one_allowed():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("GPL-3.0 OR Apache-2.0", allowed_licenses) is True


def test_spdx_simple_expressions_or_none_allowed():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("BSD-4-Clause OR GPL-3.0", allowed_licenses) is False


def test_spdx_simple_expressions_and_both_allowed():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("MIT AND BSD-3-Clause", allowed_licenses) is True


def test_spdx_simple_expressions_and_one_allowed():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("MIT AND GPL-3.0", allowed_licenses) is False


def test_spdx_simple_expressions_and_other_one_allowed():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("GPL-3.0 AND BSD-3-Clause", allowed_licenses) is False


def test_spdx_multiple_operators_expressions_only_or_all_allowed():

    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]

    assert spdx_logic("MIT OR Apache-2.0 OR BSD-3-Clause", allowed_licenses) is True


def test_spdx_multiple_operators_expressions_all_or_some_allowed():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("MIT OR GPL-3.0 OR BSD-3-Clause", allowed_licenses) is True


def test_spdx_multiple_operators_expressions_all_or_none_allowed():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("GPL-2.0 OR GPL-3.0 OR LGPL-2.1", allowed_licenses) is False


def test_spdx_multiple_operators_expressions_all_and_all_allowed():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("MIT AND Apache-2.0 AND BSD-3-Clause", allowed_licenses) is True


def test_spdx_multiple_operators_expressions_all_and_some_allowed():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("MIT AND Apache-2.0 AND GPL-3.0", allowed_licenses) is False


@pytest.mark.parametrize(
    "license_expression",
    [
        "MIT AND GPL-3.0 OR BSD-3-Clause",
        "GPL-2.0 AND GPL-3.0 OR BSD-3-Clause",
        "BSD-3-Clause OR GPL-2.0 AND GPL-3.0",
    ],
)
def test_spdx_multiple_operators_expressions_and_or_combined_positive(
    license_expression,
):
    # D.4.5 Order of precedence and parentheses
    # AND should be resolved before OR

    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic(license_expression, allowed_licenses) is True


@pytest.mark.parametrize(
    "license_expression",
    ["GPL-2.0 OR GPL-3.0 AND BSD-3-Clause", "GPL-3.0 AND BSD-3-Clause OR GPL-2.0"],
)
def test_spdx_multiple_operators_expressions_and_or_combined_negative(
    license_expression,
):
    # D.4.5 Order of precedence and parentheses
    # AND should be resolved before OR

    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic(license_expression, allowed_licenses) is False


@pytest.mark.parametrize(
    "license_expression",
    [
        "(MIT OR Apache-2.0) AND BSD-3-Clause",
        "BSD-3-Clause AND (MIT OR Apache-2.0)",
        "(MIT OR GPL-3.0) AND BSD-3-Clause",
        "BSD-3-Clause AND (MIT OR GPL-3.0)",
    ],
)
def test_spdx_single_level_brackets_expressions_pass(license_expression):
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]

    assert spdx_logic(license_expression, allowed_licenses) is True


@pytest.mark.parametrize(
    "license_expression",
    [
        "(MIT OR BSD-3-Clause) AND GPL-3.0",
        "GPL-3.0 AND (MIT OR BSD-3-Clause)",
        "GPL-3.0 OR (GPL-2.0 AND BSD-3-Clause)",
        "MIT AND (GPL-2.0 OR GPL-3.0)",
    ],
)
def test_spdx_single_level_brackets_expressions_fail(license_expression):
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]

    assert spdx_logic(license_expression, allowed_licenses) is False


@pytest.mark.parametrize(
    "license_name",
    [
        'BSD 4-Clause "Original" or "Old" License',
        'BSD 3-Clause "New" or "Revised" License',
        "GNU Affero General Public License v1.0 or later",
        "Historical Permission Notice and Disclaimer (HPND)",
        "FSF Unlimited License (With License Retention and Warranty Disclaimer)",
    ],
)
def test_spdx_licenses_with_and_or_in_name(license_name):
    allowed_licenses = [license_name]

    assert spdx_logic(license_name, allowed_licenses) is True
