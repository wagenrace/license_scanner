from src.license_scanner.get_all_packages import get_all_package_names


def test_get_all_package_names():
    try:
        import numpy  # noqa: F401
    except ImportError:
        raise ImportError(
            "The requirements.txt for the integration tests must be installed"
        )

    packages = get_all_package_names()
    assert "numpy" in packages
