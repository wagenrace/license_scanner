from src.license_scanner.get_all_packages import get_all_package_names
import pytest


@pytest.mark.parametrize(
    "model_name",
    ["numpy", "mergedeep", "absl_py", "scikit_image", "jaraco.text", "pillow", "uv"],
)
def test_get_all_package_names(model_name):
    packages = get_all_package_names()
    assert model_name in packages
