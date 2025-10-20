from src.license_scanner.parse_license import parse_license


def spdx_logic(license_expression: str, allowed_licenses: list[str]) -> bool:
    """Evaluate the SPDX license expression against the allowed licenses.
    These are expressions like "MIT OR Apache-2.0" or "GPL-3.0 AND (BSD-3-Clause OR MIT)".

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

    parsed_license = parse_license(license_expression)
    return parsed_license in allowed_licenses
