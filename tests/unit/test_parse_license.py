import warnings
from src.license_scanner.parse_license import parse_license
from src.license_scanner.parse_license.licenses_synonyms import (
    unknown_license,
    mit_license,
    gnu_lesser_general_public_license_v2_0_only,
    apache_license_v2,
)


def test_parse_license_empty_string():
    assert parse_license("") is None


def test_parse_license_none():
    assert parse_license(None) is None


def test_parse_license_with_newline():
    license_text = "This is a full license\nwith multiple lines\nand more content"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = parse_license(license_text)

        assert result is None
        assert len(w) == 1
        assert "It seems like a full license" in str(w[0].message)


def test_parse_license_strips_whitespace():
    result = parse_license("  MIT  ")
    assert result == mit_license


def test_parse_license_mit():
    result = parse_license("MIT")
    assert result == mit_license


def test_parse_gnu_lesser_gpl_v2():
    result = parse_license("GNU Lesser General Public License v2.0 only")
    assert result == gnu_lesser_general_public_license_v2_0_only


def test_parse_license_handles_copyright():
    result = parse_license("MIT copyright (c) 2023 John Doe")
    assert result == mit_license


def test_parse_license_not_found_in_synonyms():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = parse_license("a License not in the list")

        assert result == "a license not in the list"
        assert len(w) == 1
        assert 'The license "a license not in the list" was not found' in str(
            w[0].message
        )


def test_parse_license_not_found_in_synonyms_normalized():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        license1 = "a License not in the list"
        license2 = "   A LiceNse not in the lisT   "
        result1 = parse_license(license1)
        result2 = parse_license(license2)

        assert result1 == "a license not in the list"
        assert result2 == result1
        assert len(w) == 2
        assert f'The license "{license1.lower().strip()}" was not found' in str(
            w[0].message
        )
        assert f'The license "{license2.lower().strip()}" was not found' in str(
            w[1].message
        )


def test_parse_license_case_insensitive():
    result = parse_license("APACHE 2.0")
    assert result == apache_license_v2


def test_parse_license_empty_after_processing():
    result = parse_license("Copyright (c) 2023")
    assert result == unknown_license
