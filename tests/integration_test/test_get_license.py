from src.license_scanner.get_all_licenses import get_licenses, parse_license
from src.license_scanner.parse_license.licenses_synonyms import (
    mit_license,
    bsd_license,
    apache_license_v2,
    apache_license,
    mit_cmu,
    historical_permission_notice,
)
import pytest
import sys
import re

PYTHON_MINOR_VERSION = int(re.findall(r"3.(\d+).\d+", sys.version)[0])


@pytest.mark.parametrize("model_name", ["mergedeep", "jaraco.text"])
def test_get_licenses_mit(model_name):
    licenses = get_licenses(model_name)
    licenses = [parse_license(i) for i in licenses]
    assert mit_license in licenses


@pytest.mark.parametrize("model_name", ["numpy", "scikit_image"])
def test_get_licenses_general_bsd(model_name):
    licenses = get_licenses(model_name)
    licenses = [parse_license(i) for i in licenses]
    assert bsd_license in licenses


@pytest.mark.parametrize("model_name", ["absl_py"])
def test_get_licenses_apache(model_name):
    licenses = get_licenses(model_name)
    licenses = [parse_license(i) for i in licenses]
    assert apache_license_v2 in licenses


def test_get_dual_license():
    licenses = get_licenses("uv")
    licenses = [parse_license(i) for i in licenses]
    assert mit_license in licenses
    assert apache_license in licenses


def test_get_licenses_pillow():
    licenses = get_licenses("pillow")
    licenses = [parse_license(i) for i in licenses]

    # Pillow change there license in version 11
    # Python 3.13 and up will have the new version of Pillow
    if PYTHON_MINOR_VERSION <= 12:
        assert historical_permission_notice in licenses
    else:
        assert mit_cmu in licenses
