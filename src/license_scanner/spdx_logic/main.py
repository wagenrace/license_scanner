from src.license_scanner.parse_license import parse_license


def _split_expression(license_expression: str) -> list[str]:
    """Split the license expression into parts based on the first operator found (AND/OR).

    :param license_expression: The SPDX license expression to split.
    :type license_expression: str
    :return: List containing the parts of the expression split by the first operator.
    :rtype: list[str]
    """
    license_expression = license_expression.lower().strip()
    pos_first_and = license_expression.find(" and ")
    pos_first_or = license_expression.find(" or ")

    if pos_first_and != -1 and pos_first_and < pos_first_or:
        # First operator is AND
        first_part = license_expression[:pos_first_and]
        second_part = license_expression[pos_first_and + 5 :]
        return [first_part, "AND"] + _split_expression(second_part)
    elif pos_first_or != -1 and pos_first_or < pos_first_and:
        # First operator is OR
        first_part = license_expression[:pos_first_or]
        second_part = license_expression[pos_first_or + 4 :]
        return [first_part, "OR"] + _split_expression(second_part)
    else:
        return [license_expression]


def spdx_logic(license_expression: str, allowed_licenses: list[str]) -> bool:
    """Evaluate the SPDX license expression against the allowed licenses.
    These are expressions like "MIT OR Apache-2.0" or "GPL-3.0 AND (BSD-3-Clause OR MIT)".

    This follows: https://spdx.github.io/spdx-spec/v2.3/SPDX-license-expressions/

    :param license_expression: The SPDX license expression to evaluate.
    :type license_expression: str
    :param allowed_licenses: The list of allowed licenses.
    :type allowed_licenses: list[str]
    :return: True if the license expression is valid, False otherwise.
    :rtype: bool
    """

    allowed_licenses = [parse_license(lic) for lic in allowed_licenses]

    if not allowed_licenses:
        return False

    license_expression = license_expression.lower().strip()
    split_expression = _split_expression(license_expression)
    if len(split_expression) == 1:
        # Single license
        parsed_license = parse_license(split_expression[0])
        return parsed_license in allowed_licenses
