# license_scanner

[![Downloads](https://static.pepy.tech/badge/license-scanner)](https://pepy.tech/project/license-scanner)

Find all licenses needed by the package in your python environment.
It will sort all package by license.

Install by pip

```cmd
pip install license_scanner
```

Usage

```cmd
license_scanner
```

![](readme_files/demo.gif)

## Check within you pipeline

You can make your pipeline fail if a project does not have the correct licenses.
To do so create a `pyproject.toml` and add underneath `tool.license_scanner` two lists `allowed-licenses` and `allowed-packages`.
If a package does not have license in `allowed-licenses` AND it is not in `allowed-packages` it will throw an error.

```toml
[tool.license_scanner]
allowed-licenses = [
  "MIT",
  "apache software license",
  "apache software license v2",
  "apache software license v3",
  "BSD license",
  "BSD 3-clause license",
  'GNU lesser general public license',
  'GNU lesser general public license v2',
  'GNU lesser general public license v3',
  'Python software foundation license',
  'Mozilla public license 2.0 (mpl 2.0)',
  'mozilla',
]
allowed-packages = ["license_scanner"]
```

To run the license scanner make sure you are in the same directory as `pyproject.toml` and run `license_scanner -m whitelist` or `python -m license_scanner -m whitelist`. 
It will now throw you an error if your environment has an package with a license you did not approve of.

### Example: Github actions

This github actions triggers every time you make a PR to the main branch. With `pip install .` it installs the current project, next it installs `license_scanner`, and lastly it runs the check.

Be aware, if you want to do unittest make sure you install `pytest` AFTER you run license_scanner. Otherwise `pytest` is in your environment when you check for unwanted licenses.

```yaml
name: Licenses check

on:
  pull_request:
    branches:
      - main

permissions:
  contents: read

jobs:
  deploy:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.x'
    - name: Check for licenses
      run: |
        python -m pip install --upgrade pip
        pip install .
        pip install license_scanner
        python -m license_scanner -m whitelist

```

## Supported licenses

- Apache license
- Apache license 1.0
- Apache license 2.0
- Azure License
- BSD license
- BSD 0-clause license
- BSD 2-clause license
- BSD 3-clause license
- BSD 4-clause license
- Creative Commons Zero, CC-0
- Eclipse public license 1.0 (epl-1.0)
- Eclipse public license 2.0 (epl-2.0)
- GNU Affero general public license (apl)
- GNU Affero general public license v3 (aplv3)
- GNU lesser general public license
- GNU lesser general public license v2 (lgplv2)
- GNU lesser general public license v3 (lgplv3)
- GNU general public license
- GNU general public license v2 (gplv2)
- GNU general public license v3 (gplv3)
- Historical Permission Notice and Disclaimer (HPND)
- ISC license (iscl)
- MIT license
- MIT No Attribution
- Mozilla public license (mpl)
- Mozilla public license 2.0 (mpl 2.0)
- Public domain
- Python software foundation license
- Repoze public license
- The Unlicense (Unlicense)
- DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
- Zope Public License
- Zope Public License v1
- Zope Public License v2
# Credits

- Tom Nijhof
