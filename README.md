# license_scanner

# Creating a package

Fork this repo.
Next up make sure there are 2 remote repositories connected.
In vscode:

- ctrl + shift + P
- Git: Add remote
- `origin_basic_function_package`
- `https://cytosmart.visualstudio.com/CytoSmartImageAnalysis/_git/basic_function_package`

Next steps are only if you need to connect it to an existing repo.

- Open terminal (ctrl + shift + `)
- git pull origin_basic_function_package master --allow-unrelated-histories

You now can `git > pull from..` and choose to pull from `origin` or `origin_basic_function_package`.
By choosing `origin_basic_function_package` you will update your package.

# Rename variables

- Search for 'license_scanner' and replace it with the package name of your choosing.
- - Don't forget to change the folder name too!
- Search for 'Tom Nijhof' and replace it with your name.
- Search for 'Scans your environment for all needed licenses' and replace it with a small description of what the package does

# Adding code to the package

The **init**.py will be used to navigate easily through functions.
You can also add a function of collection.

You import the whole function in license_scanner.**init**.py.
Every function has its own folder.
Within this folder is a:

- `main.py` for the function itself.
- `__init__.py` for importing the code
- `test_FUNCTION_NAME.py` for the unit tests

Example **function**:

```
# license_scanner folder
- __init__.py
-- from .FUNCTION_NAME import FUNCTION_NAME
- FUNCTION_NAME (folder)
-- __init__.py
--- from .main import FUNCTION_NAME
-- main.py
--- def FUNCTION_NAME(...):
-- test_FUNCTION_NAME.py
--- class test_FUNCTION_NAME(TestCase)
```

This will import all function on COLLECTION_NAME to license_scanner.
Using license_scanner will now look like this

```
# Using of license_scanner
from license_scanner import FUNCTION_NAME
```

Example **collection**:

```
# license_scanner folder
- __init__.py
-- from .FUNCTION_NAME import FUNCTION_NAME
- FUNCTION_NAME (folder)
-- __init__.py
--- from .main import FUNCTION_NAME
-- main.py
--- def FUNCTION_NAME(...):
-- test_FUNCTION_NAME.py
--- class test_FUNCTION_NAME(TestCase)
```

This will import all function on COLLECTION_NAME to license_scanner.
Using license_scanner will now look like this

```
# Using of license_scanner
from license_scanner.COLLECTION_NAME import FUNCTION_NAME
```

# testing the build of your package

To test if you function build correctly open your terminal.

- Go to the root folder of your package (where setup.py is located)
- run 'python setup.py sdist'

You will now get a /dist/license_scanner-0.0.1.tar.gz

- copy its location
- create a new empty python environment (e.q. conda create -n NAMENEWENV python=3.7)
- Go in this new env (e.q. conda activate NAMENEWENV)
- Install your package (pip install [pathToPackage]/dist/license_scanner-0.0.1.tar.gz)
- Try importing function from your package
- - python
- - from license_scanner import license_scanner
- - license_scanner.calculate
- - should return <function license_scanner.calculate at [pointer]>
- - expands these test to make sure it works
- Possible errors:
- - missing package [depPackage]
- - - add [depPackage] to setup.py -> requirements
- - ImportError: cannot import name 'license_scanner'
- - - check if **init**.py imports the function

# testing your code

You should have writing some unit test well creating your functions.
In order to run them you can use pytest in the terminal or with the vscode extension.

# setup build pipeline

The file 'azure-pipelines.yml' contains the full pipeline.

- To activate it go to devops (cytosmart.visualstudio.com)
- goto Pipelines -> builds -> new -> new build pipeline
- Select your repo
- Done
- possible errors
- - pytest 1 error code '5'
- - - This happens if you have zero unit tests

# Last step

Delete all instruction from `creating a package` till here.

# Usage

Scans your environment for all needed licenses

# Install

To install this package follow the these steps:

    1. Create/Edit your pip configuration file:
            a. Windows users: %APPDATA%\pip\pip.ini
            b. MacOS users: $HOME/Library/Application Support/pip/pip.conf
                if directory $HOME/Library/Application Support/pip exists
                else $HOME/.config/pip/pip.conf
            c. Linux users: $HOME/.config/pip/pip.conf

    For windows. Make sure you create the file via vscode.
    If not the file might become a text document.

![Wrong](README_images/correct_ini.png)

    2. Get access token
       1. Go to User Settings > Personal Access Token
       2. New Token
       3. Set a name
       4. Set expiration date (max a year in the future)
       5. Give code Read & Write Access
       6. Give packing Read Access
       7. Create
       8. Copy token

![Gif](README_images/get_acces_token.gif)

    3. Open pip.ini and add

```
[global]
extra-index-url=https://ImageAnalysisArtifacts:ACCESTOKEN@cytosmart.pkgs.visualstudio.com/_packaging/ImageAnalysisArtifacts@Local/pypi/simple/
```

    Replace the ACCESTOKEN for what you copied in step 2

    4. DONE

# Features

-

# Credits

- Tom Nijhof
