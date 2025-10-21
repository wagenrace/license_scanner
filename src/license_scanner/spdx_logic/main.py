import re
import warnings
from src.license_scanner.parse_license import parse_license


def _split_expression(license_expression: str) -> list[str]:
    """Split the license expression into parts based on the first operator found (AND/OR).

    :param license_expression: The SPDX license expression to split.
    :type license_expression: str
    :return: List containing the parts of the expression split by the first operator.
    :rtype: list[str]
    """

    if "(" in license_expression:
        # Dealing with brackets
        # This will split Q OR (A AND (B OR C)) AND D into ['Q', 'OR', 'A AND (B OR C)', 'AND', 'D']

        # Number opening and closing brackets should match
        if license_expression.count("(") != license_expression.count(")"):
            warnings.warn("Unmatched parentheses in license expression.", UserWarning)
            return [license_expression]

        # Find the first opening bracket
        search_opening_bracket = re.search(r"\(", license_expression)
        start_index = search_opening_bracket.start()
        end_index = search_opening_bracket.end()
        number_of_brackets = 1

        # Find the matching closing bracket
        # Handle nested brackets as well; e.g., Q OR (A AND (B OR C))
        while number_of_brackets > 0:
            next_char = license_expression[end_index]
            if next_char == "(":
                number_of_brackets += 1
            elif next_char == ")":
                number_of_brackets -= 1
            end_index += 1

        # Split the string in 3 parts, before, between and after the brackets
        first_part = license_expression[:start_index]
        part_between_brackets = license_expression[start_index + 1 : end_index - 1]
        last_part = license_expression[end_index:]

        # Recursively split the parts
        return_values = []
        if first_part.strip():
            # If there is something before the brackets
            # It will still need to be split
            # because even with brackets there can be operators (AND, OR) before
            return_values += _split_expression(first_part)
        return_values.append(part_between_brackets.strip())
        if last_part.strip():
            # Something after the brackets can have brackets too
            # So recursively split it
            return_values += _split_expression(last_part)
        return return_values

    license_expression_norm = license_expression.lower()
    pos_first_and = license_expression_norm.find(" and ")
    pos_first_or = license_expression_norm.find(" or ")

    if pos_first_and != -1 and (pos_first_and < pos_first_or or pos_first_or == -1):
        # First operator is AND
        first_part = license_expression[:pos_first_and]
        second_part = license_expression[pos_first_and + 5 :]
        return_values = [first_part, "AND"] + _split_expression(second_part)
    elif pos_first_or != -1 and (pos_first_or < pos_first_and or pos_first_and == -1):
        # First operator is OR
        first_part = license_expression[:pos_first_or]
        second_part = license_expression[pos_first_or + 4 :]
        return_values = [first_part, "OR"] + _split_expression(second_part)
    else:
        return_values = [license_expression]

    return_values = [part for part in return_values if part]
    return return_values


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
