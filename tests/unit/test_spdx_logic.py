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


def test_spdx_simple_expressions1():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]

    assert spdx_logic("MIT OR Apache-2.0", allowed_licenses) is True


def test_spdx_simple_expressions2():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("MIT OR GPL-3.0", allowed_licenses) is True


def test_spdx_simple_expressions3():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("BSD-4-Clause OR GPL-3.0", allowed_licenses) is False


def test_spdx_simple_expressions4():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("MIT AND BSD-3-Clause", allowed_licenses) is True


def test_spdx_simple_expressions5():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("MIT AND GPL-3.0", allowed_licenses) is False


def test_spdx_multiple_operators_expressions1():
    # D.4.5 Order of precedence and parentheses
    # AND should be resolved before OR

    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]

    assert spdx_logic("MIT OR Apache-2.0 OR BSD-3-Clause", allowed_licenses) is True


def test_spdx_multiple_operators_expressions2():
    # D.4.5 Order of precedence and parentheses
    # AND should be resolved before OR

    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("MIT OR GPL-3.0 OR BSD-3-Clause", allowed_licenses) is True


def test_spdx_multiple_operators_expressions3():
    # D.4.5 Order of precedence and parentheses
    # AND should be resolved before OR

    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("GPL-2.0 OR GPL-3.0 OR LGPL-2.1", allowed_licenses) is False


def test_spdx_multiple_operators_expressions4():
    # D.4.5 Order of precedence and parentheses
    # AND should be resolved before OR

    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("MIT AND Apache-2.0 AND BSD-3-Clause", allowed_licenses) is True


def test_spdx_multiple_operators_expressions5():
    # D.4.5 Order of precedence and parentheses
    # AND should be resolved before OR

    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("MIT AND Apache-2.0 AND GPL-3.0", allowed_licenses) is False
    # AND is resolved before OR:


def test_spdx_multiple_operators_expressions6():
    # D.4.5 Order of precedence and parentheses
    # AND should be resolved before OR

    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("MIT AND GPL-3.0 OR BSD-3-Clause", allowed_licenses) is True


def test_spdx_multiple_operators_expressions7():
    # D.4.5 Order of precedence and parentheses
    # AND should be resolved before OR

    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("GPL-2.0 AND GPL-3.0 OR BSD-3-Clause", allowed_licenses) is True


def test_spdx_multiple_operators_expressions8():
    # D.4.5 Order of precedence and parentheses
    # AND should be resolved before OR

    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("BSD-3-Clause OR GPL-2.0 AND GPL-3.0", allowed_licenses) is True


def test_spdx_multiple_operators_expressions9():
    # D.4.5 Order of precedence and parentheses
    # AND should be resolved before OR

    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("GPL-2.0 OR GPL-3.0 AND BSD-3-Clause", allowed_licenses) is False


def test_spdx_multiple_operators_expressions10():
    # D.4.5 Order of precedence and parentheses
    # AND should be resolved before OR

    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("GPL-3.0 AND BSD-3-Clause OR GPL-2.0", allowed_licenses) is False


def test_spdx_single_level_brackets_expressions1():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]

    assert spdx_logic("(MIT OR Apache-2.0) AND BSD-3-Clause", allowed_licenses) is True


def test_spdx_single_level_brackets_expressions2():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("BSD-3-Clause AND (MIT OR Apache-2.0)", allowed_licenses) is True


def test_spdx_single_level_brackets_expressions3():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("(MIT OR GPL-3.0) AND BSD-3-Clause", allowed_licenses) is True


def test_spdx_single_level_brackets_expressions4():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("BSD-3-Clause AND (MIT OR GPL-3.0)", allowed_licenses) is True


def test_spdx_single_level_brackets_expressions5():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("(MIT OR BSD-3-Clause) AND GPL-3.0", allowed_licenses) is False


def test_spdx_single_level_brackets_expressions6():
    allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    assert spdx_logic("GPL-3.0 AND (MIT OR BSD-3-Clause)", allowed_licenses) is False
