import argparse
import sys
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

from .get_all_licenses import get_all_licenses
from .parse_license import parse_license
from .parse_license.licenses_synonyms import unknown_license

if sys.version_info >= (3, 11):
    try:
        import tomllib
    except ImportError:
        # Help users on older alphas
        if not TYPE_CHECKING:
            import tomli as tomllib
else:
    import tomli as tomllib


class Mode(Enum):
    whitelist = "whitelist"
    print = "print"
    blacklist = "blacklist"


def parse_pyproject_toml() -> Dict[str, Any]:
    """Parse a pyproject toml file, pulling out relevant parts for Black.

    If parsing fails, will raise a tomllib.TOMLDecodeError.
    """
    path_pyproject_toml = Path.cwd() / "pyproject.toml"
    with open(path_pyproject_toml, "rb") as f:
        pyproject_toml = tomllib.load(f)
    config: Dict[str, Any] = pyproject_toml.get("tool", {}).get("license_scanner", {})
    config = {k.replace("--", "").replace("-", "_"): v for k, v in config.items()}

    return config


def __get_arguments() -> Mode:
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
    return mode


def main():
    """
    Get all the installed packages and licenses.
    If will use the system argument -m or --mode to determine what to do with it.

    Mode: print (default)
        Prints the packages sorted by license
    Mode: Whitelist
        Gives an error if one of packages and it licenses are not whitelisted
        Whitelist are loaded from pyproject.toml -- allowed-licenses && allowed-packages
    """

    mode = __get_arguments()

    all_licenses = get_all_licenses()

    all_used_licenses = list(all_licenses.keys())
    all_used_licenses.sort()

    if mode == Mode.print:
        for key in all_used_licenses:
            print(f"\n ======\n {key} \n ======")
            for _license in all_licenses[key]:
                print(f" - {_license}")

    elif mode == Mode.whitelist:
        pyproject_config = parse_pyproject_toml()

        raw_allowed_licenses = pyproject_config.get("allowed_licenses", [])
        allowed_licenses = [parse_license(i) for i in raw_allowed_licenses]
        if None in all_licenses:
            allowed_licenses.remove(None)
        raw_allowed_packages = pyproject_config.get("allowed_packages", [])
        allowed_packages = [i.lower() for i in raw_allowed_packages]

        problem_packages = []

        for used_license in all_used_licenses:
            if not used_license in allowed_licenses:
                for package in all_licenses[used_license]:
                    if package not in allowed_packages:
                        problem_packages.append((package, used_license))

        if problem_packages:
            for package, license in problem_packages:
                if license == unknown_license:
                    print(
                        f"{package} license could not be found. If this is a error please report at https://github.com/wagenrace/license_scanner/issues if you want to ignore this package add it to the whitelist in pyproject.toml"
                    )
                else:
                    print(f"{package} with {license} is NOT whitelisted")
            raise ValueError(
                "Some of the packages found do not use white listed licenses"
            )
        else:
            print("=+=+=+=+= All packages are good to use =+=+=+=+=")


if __name__ == "__main__":
    main()
