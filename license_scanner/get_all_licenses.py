#%%
from pkg_resources import working_set
from .parse_license import parse_license


def get_all_licenses():
    all_licenses = {}
    for key in working_set.normalized_to_canonical_keys:
        """
        The metadata of a package is stored in "metadata" or "PKG-INFO"
        """
        try:
            package_name = working_set.normalized_to_canonical_keys[key]
            package = working_set.by_key[package_name]
            metadata_lines = package.get_metadata("METADATA").split("\n")
        except:
            try:
                metadata_lines = package.get_metadata("PKG-INFO").split("\n")
            except:
                all_licenses["Unknown"] = all_licenses.get("Unknown", []) + [key]
                continue

        # You can get the license from license argument or classifier
        license_arg = None
        license_classifier = None
        for line in metadata_lines:
            line: str = line
            if line.startswith("License: "):
                license_arg = line.replace("License: ", "")
            if line.startswith("Classifier: License ::"):
                license_classifier = line.split(" :: ")[-1]
                if license_classifier.lower() in ["osi approved"]:
                    license_classifier = None

        general_license = "NOT FOUND"
        license_arg = parse_license(license_arg)
        license_classifier = parse_license(license_classifier)

        # You can get the license from license argument or classifier
        if license_classifier:
            general_license = license_classifier
        elif license_arg is not None and license_arg != "UNKNOWN":
            general_license = license_arg

        all_licenses[general_license] = all_licenses.get(general_license, []) + [key]

    return all_licenses
