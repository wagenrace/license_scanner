from src.license_scanner.spdx_logic.main import _split_expression


def test_split_expression_happy_flow1():

    assert _split_expression("MIT AND Apache-2.0") == [
        "MIT",
        "AND",
        "Apache-2.0",
    ]


def test_split_expression_happy_flow2():

    assert _split_expression("MIT OR Apache-2.0") == [
        "MIT",
        "OR",
        "Apache-2.0",
    ]


def test_split_expression_happy_flow3():

    assert _split_expression("MIT") == ["MIT"]


def test_split_expression_happy_flow4():

    assert _split_expression("MIT AND Apache-2.0 OR BSD-3-Clause") == [
        "MIT",
        "AND",
        "Apache-2.0",
        "OR",
        "BSD-3-Clause",
    ]


def test_split_expression_happy_flow5():

    assert _split_expression("MIT OR Apache-2.0 AND BSD-3-Clause") == [
        "MIT",
        "OR",
        "Apache-2.0",
        "AND",
        "BSD-3-Clause",
    ]


def test_split_partly_expression1():

    assert _split_expression(" AND Apache-2.0") == [
        "AND",
        "Apache-2.0",
    ]


def test_split_partly_expression2():
    assert _split_expression(" OR Apache-2.0") == [
        "OR",
        "Apache-2.0",
    ]


def test_split_partly_expression3():
    assert _split_expression("") == []


def test_split_partly_expression4():
    assert _split_expression("MIT AND Apache-2.0 OR ") == [
        "MIT",
        "AND",
        "Apache-2.0",
        "OR",
    ]


def test_split_partly_expression5():
    assert _split_expression("MIT OR Apache-2.0 AND ") == [
        "MIT",
        "OR",
        "Apache-2.0",
        "AND",
    ]


def test_split_expression_pure_brackets():
    assert _split_expression("(MIT AND Apache-2.0)") == ["MIT AND Apache-2.0"]


def test_split_expression_brackets_and_not():

    assert _split_expression("(MIT OR Apache-2.0) AND BSD-3-Clause") == [
        "MIT OR Apache-2.0",
        "AND",
        "BSD-3-Clause",
    ]


def test_split_expression_brackets_nested_brackets():

    assert _split_expression(
        "BSD-3-Clause AND ((MIT OR BSD-3-Clause) OR Apache-2.0)"
    ) == ["BSD-3-Clause", "AND", "(MIT OR BSD-3-Clause) OR Apache-2.0"]


def test_split_expression_multiple_brackets():

    assert _split_expression("(MIT OR Apache-2.0) OR (BSD-3-Clause AND MIT)") == [
        "MIT OR Apache-2.0",
        "OR",
        "BSD-3-Clause AND MIT",
    ]


def test_split_expression_multiple_and_nested_brackets():

    assert _split_expression(
        "(MIT OR Apache-2.0) OR ((MIT OR BSD-3-Clause) OR Apache-2.0)"
    ) == ["MIT OR Apache-2.0", "OR", "(MIT OR BSD-3-Clause) OR Apache-2.0"]
