from src.license_scanner.spdx_logic.main import spdx_logic, _split_expression


def test_spdx_single_license():
    allowed_licenses = [
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "completely unknown license",
    ]

    # SPDX named licenses
    assert spdx_logic("MIT", allowed_licenses) is True
    assert spdx_logic("Apache-2.0", allowed_licenses) is True
    assert spdx_logic("BSD-3-Clause", allowed_licenses) is True
    assert spdx_logic("GPL-3.0", allowed_licenses) is False

    # License NOT named in SPDX, but present in allowed licenses
    assert spdx_logic("MIT license", allowed_licenses) is True
    assert spdx_logic("BSD 3-clause license", allowed_licenses) is True
    assert spdx_logic("GPL version 3", allowed_licenses) is False
    assert spdx_logic("mit 0", allowed_licenses) is False

    # License NOT named in SPDX and NOT present in allowed licenses
    assert spdx_logic("completely unknown license", allowed_licenses) is True
    assert spdx_logic("another unknown license", allowed_licenses) is False


def test_spdx_simple_expressions():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]

    assert spdx_logic("MIT OR Apache-2.0", allowed_licenses) is True
    assert spdx_logic("MIT OR GPL-3.0", allowed_licenses) is True
    assert spdx_logic("BSD-4-Clause OR GPL-3.0", allowed_licenses) is False
    assert spdx_logic("MIT AND BSD-3-Clause", allowed_licenses) is True
    assert spdx_logic("MIT AND GPL-3.0", allowed_licenses) is False


def test_spdx_multiple_operators_expressions():
    # D.4.5 Order of precedence and parentheses
    # AND should be resolved before OR

    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]

    assert spdx_logic("MIT OR Apache-2.0 OR BSD-3-Clause", allowed_licenses) is True
    assert spdx_logic("MIT OR GPL-3.0 OR BSD-3-Clause", allowed_licenses) is True
    assert spdx_logic("GPL-2.0 OR GPL-3.0 OR LGPL-2.1", allowed_licenses) is False
    assert spdx_logic("MIT AND Apache-2.0 AND BSD-3-Clause", allowed_licenses) is True
    assert spdx_logic("MIT AND Apache-2.0 AND GPL-3.0", allowed_licenses) is False
    # AND is resolved before OR:
    assert spdx_logic("MIT AND GPL-3.0 OR BSD-3-Clause", allowed_licenses) is True
    assert spdx_logic("GPL-2.0 AND GPL-3.0 OR BSD-3-Clause", allowed_licenses) is True
    assert spdx_logic("BSD-3-Clause OR GPL-2.0 AND GPL-3.0", allowed_licenses) is True
    assert spdx_logic("GPL-2.0 OR GPL-3.0 AND BSD-3-Clause", allowed_licenses) is False
    assert spdx_logic("GPL-3.0 AND BSD-3-Clause OR GPL-2.0", allowed_licenses) is False


def test_spdx_single_level_brackets_expressions():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]

    assert spdx_logic("(MIT OR Apache-2.0) AND BSD-3-Clause", allowed_licenses) is True
    assert spdx_logic("BSD-3-Clause AND (MIT OR Apache-2.0)", allowed_licenses) is True
    assert spdx_logic("(MIT OR GPL-3.0) AND BSD-3-Clause", allowed_licenses) is True
    assert spdx_logic("BSD-3-Clause AND (MIT OR GPL-3.0)", allowed_licenses) is True
    assert spdx_logic("(MIT OR BSD-3-Clause) AND GPL-3.0", allowed_licenses) is False
    assert spdx_logic("GPL-3.0 AND (MIT OR BSD-3-Clause)", allowed_licenses) is False


def test_split_expression():

    assert _split_expression("MIT AND Apache-2.0") == [
        "MIT",
        "AND",
        "Apache-2.0",
    ]
    assert _split_expression("MIT OR Apache-2.0") == [
        "MIT",
        "OR",
        "Apache-2.0",
    ]
    assert _split_expression("MIT") == ["MIT"]
    assert _split_expression("MIT AND Apache-2.0 OR BSD-3-Clause") == [
        "MIT",
        "AND",
        "Apache-2.0",
        "OR",
        "BSD-3-Clause",
    ]
    assert _split_expression("MIT OR Apache-2.0 AND BSD-3-Clause") == [
        "MIT",
        "OR",
        "Apache-2.0",
        "AND",
        "BSD-3-Clause",
    ]
