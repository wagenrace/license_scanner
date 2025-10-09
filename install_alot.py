import requests
import subprocess

top_packages_url = (
    r"https://hugovk.github.io/top-pypi-packages/top-pypi-packages.min.json"
)

top_packages = requests.get(top_packages_url).json()

all_packages = [i["project"] for i in top_packages["rows"]]

for package in all_packages:
    subprocess.run(f"pip install {package}")
