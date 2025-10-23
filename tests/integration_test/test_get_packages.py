from src.license_scanner.get_all_packages import get_all_package_names


def test_get_all_package_names():
    try:
        import numpy  # noqa: F401
        import absl  # noqa: F401
        import skimage  # noqa: F401
        import jaraco.text  # noqa: F401
        import mergedeep  # noqa: F401
    except ImportError:
        raise ImportError(
            "The requirements.txt for the integration tests must be installed"
        )

    packages = get_all_package_names()
    assert "numpy" in packages
    assert "mergedeep" in packages
    # Package name and import name differ
    assert "absl_py" in packages
    assert "scikit_image" in packages
    # Package not found by setuptools at the time
    assert "jaraco.text" in packages
