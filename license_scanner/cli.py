import argparse
from enum import Enum
from pathlib import Path
import tomllib
from typing import Any, Dict


class Mode(Enum):
    whitelist = "whitelist"
    print = "print"
    blacklist = "blacklist"


from license_scanner.get_all_licenses import get_all_licenses


def parse_pyproject_toml() -> Dict[str, Any]:
    """Parse a pyproject toml file, pulling out relevant parts for Black.

    If parsing fails, will raise a tomllib.TOMLDecodeError.
    """
    path_pyproject_toml = Path.cwd() / "pyproject.toml"
    with open(path_pyproject_toml, "rb") as f:
        pyproject_toml = tomllib.load(f)
    config: Dict[str, Any] = pyproject_toml.get("tool", {}).get("license-scanner", {})
    config = {k.replace("--", "").replace("-", "_"): v for k, v in config.items()}

    return config


def main():
    """
    Get all the installed packages and licenses.
    Prints the packages sorted by license
    """
    parser = argparse.ArgumentParser(
        description="Just an example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=Mode,
        choices=list(Mode),
        help=f"The mode determines what to do with the results. Options are: {list(Mode)}",
        default=Mode.print,
    )
    args = parser.parse_args()
    config = vars(args)
    mode = config["mode"]

    all_licenses = get_all_licenses()

    all_keys = list(all_licenses.keys())
    all_keys.sort()

    if mode == Mode.print:
        for key in all_keys:
            print(f"\n ======\n {key} \n ======")
            for license in all_licenses[key]:
                print(f" - {license}")


if __name__ == "__main__":
    main()
