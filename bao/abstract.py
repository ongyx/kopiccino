# coding: utf8
"""Abstract representations of bao packages (buns) and repositories (bakeries).
"""

import os
import toml
import pathlib
import shutil
import tempfile
import zipfile

from bao import utils
from bao.exceptions import PackageError, RepositoryError


class Package(object):
    """A bun (bao package).
    
    Args:
        mainscript: The package's main script. All packages must have one
        script with the same name as the package
        (i.e package helloworld -> helloworld.py).
    
        metadata: Package metadata (see https://stackoverflow.com/a/1523456
        for a standard Python header format).
        
        See help(bao.extract_metadata) for auto-extraction of metadata from
        a Python script.
        
        Mandatory fields:
        
        'name' - name of package

        'author' - people who wrote the code
        
        'license' - must be a SPDX ID
        (see https://github.com/spdx/license-list-data/blob/master/json/licenses.json),
        or else it is treated as a custom license
        
        'copyright' - copyright clause
        
        'version' - semantic version of the package
        
        Optional fields:

        'doc' - description, recommended

        'maintainer' - commits bugfixes for the package

        'email' - email of maintainer
    
    Attributes:
        modules (dict): A mapping of module paths to be bundled in the package.
        metadata (namedtuple): Metadata of the package.
        mainscript (str): The main script of the package.
    
    Raises:
        KeyError: If a required field in the metadata is not specified.
    """

    def __init__(self, mainscript: str, metadata: dict):
        self.modules = []
        self.mainscript = mainscript
        self.metadata = metadata
        utils._fill_defaults(metadata, utils.PACKAGE_ATTRIBUTES)

    def add_module(self, path_to_module: str) -> None:
        """Bundle a module as a dependency in the package.
        
        Args:
            path_to_module: The path to the module. Must point to a file or a
            folder with a __init__.py file.
        
        Raises:
            PackageError: If a module could not be found at path_to_module.
        """
        # expand path first
        path_to_module = pathlib.Path(path_to_module).resolve().expanduser()

        if not utils.valid_module_path(path_to_module):
            raise PackageError(f"invalid module: '{path_to_module}'")

        self.modules.append(path_to_module)

    def build(self) -> bytes:
        """Compile the package (and optionally, the added modules) into a single ZipFile.
        
        Returns:
            bytes: the raw bytes of the Zipfile.
        """

        package_name = self.metadata["name"]
        # we use a temporary directory for shutil use
        with tempfile.TemporaryDirectory() as dir:

            # copy over modules into directory
            # TODO: find a more memory-efficient way to bundle modules instead of copying over each one
            for module_path in self.modules:
                utils.copypath(module_path, dir)

            # output the main script
            with open(pathlib.Path(dir) / package_name + ".py", mode="w") as f:
                f.write(self.mainscript)

            # zip the temporary directory contents into yet another temporary file
            with tempfile.NamedTemporaryFile() as file:
                zip_path = shutil.make_archive(file.name, "zip", root_dir=dir)

        # write metadata to zipfile as a comment
        with zipfile.ZipFile(zip_path, mode="a") as z:
            z.comment = toml.dumps(self.metadata)

        try:
            with open(zip_path, mode="rb") as f:
                return f.read()

        finally:
            # remove the temporary zipfile
            os.remove(zip_path)


class Repository(object):
    """A repository (bakery) for storing bao packages.
    
    A repository is a folder containing a zipfile for each package
    (bundled with its metadata as a comment).
    A special file called '.bakery.toml' contains metadata of all packages in the
    repository.
    
    Args:
        name: The nickname of the repository.
    
    Attributes:
        name: The repo name.
        packages: List of packages that the repo has.
    
    """

    def __init__(self, name: str):
        self.name = name
        self.packages = []

    def add_package(self, package: Package) -> None:
        """Add a package to the repository.
        
        Args:
            package: The package. Must be a (subclass of) bao.abstract.Package.
        """

        if not isinstance(package, Package):
            raise RepositoryError("package must be a subclass of bao.abstract.Package")

        else:
            self.packages.append(package)

    def build(self, path: str) -> None:
        """Compile a repository into a folder.
        
        Args:
            path: The path to the folder.
        
        Returns:
            None.
        
        Raises:
            PermissionError/IOError, if the folder is inaccessible.
        """

        metadata = {
            "reponame": self.name,
            "packages": [p.metadata for p in self.packages],
        }

        # Output metadata
        with open(".bakery.toml", mode="w") as f:
            toml.dump(metadata, f, indent=4)

        for package in self.packages:
            output_path = pathlib.Path(path) / package.name + ".zip"

            with open(output_path, mode="wb") as f:
                f.write(package.build())
