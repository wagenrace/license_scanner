#%%
from pkg_resources import working_set
from .parse_license import parse_license


def get_all_licenses():
    all_licenses = {}
    for key in working_set.normalized_to_canonical_keys:
        try:
            metadata_lines = (
                working_set.by_key[key].get_metadata("metadata").split("\n")
            )
        except:
            all_licenses["Unknown"] = all_licenses.get("Unknown", []) + [key]
            continue

        license_arg = None
        license_classifier = None
        for line in metadata_lines:
            line: str = line
            if line.startswith("License: "):
                license_arg = line.replace("License: ", "")
            if line.startswith("Classifier: License ::"):
                license_classifier = line.split(" :: ")[-1]

        general_license = "NOT FOUND"
        license_arg = parse_license(license_arg)
        license_classifier = parse_license(license_classifier)

        if license_arg is not None and license_arg != "UNKNOWN":
            general_license = license_arg
        elif license_classifier:
            general_license = license_classifier

        all_licenses[general_license] = all_licenses.get(general_license, []) + [key]

    return all_licenses
