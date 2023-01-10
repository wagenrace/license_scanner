from .get_all_licenses import get_all_licenses


def main():
    all_licenses = get_all_licenses()

    all_keys = list(all_licenses.keys())
    all_keys.sort()

    for key in all_keys:
        print(f"\n ======\n {key} \n ======")
        for license in all_licenses[key]:
            print(f" - {license}")
    # print(all_licenses)
