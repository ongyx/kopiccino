# coding: utf8
"""Abstract representations of bao packages (buns) and repositories (bakeries).

A bao package is a normal zipfile ('package.zip') plus a metadata file in TOML format
('package.toml').

The zipfile must at least have a Python script with the same name as the package
itself ('package.py'). All other Python modules (and folders with __init__.py files)
are treated as internal modules. Anything else is ignored.

It is recommended that the internal module names start with the package name,
i.e {PACKAGE_NAME}_tests, to avoid namespace pollution. If the dependency is
avaliable from Pypi or installable through pip, use the 'pip_requires' key in the
package metadata instead.

A bao repository is a folder which has one or more buns, with a central index
('BAKERY.toml') that tells bao about the packages avaliable. The index also stores
the metadata of all packages in the repository.

On creating a bakery from one or more packages, all .toml files are merged into the
'BAKERY.toml' file.
"""

import io
import os
import pathlib
import shutil
import tempfile
import toml
import zipfile

from . import utils
from .exceptions import PackageError, RepositoryError


class Package(object):
    """A bun (bao package).
    
    Args:
        mainscript: The package's main script. All packages must have one
        script with the same name as the package
        (i.e package helloworld -> helloworld.py).
    
        metadata: Package metadata (see https://stackoverflow.com/a/1523456
        for a standard Python header format).
        
        See help(bao.utils.autogen_metadata) for auto-extraction of metadata from
        a Python script.
        
        Mandatory fields (all should be a string):
        
        'name' - Name of package
        
        'author' - The people who wrote the code
        
        'license' - must be a SPDX ID
        (https://github.com/spdx/license-list-data/blob/master/json/licenses.json),
        or else it is treated as a custom license
        
        'version' - semantic version of the package
        
        Optional fields:

        'doc' - description, recommended
    
    Attributes:
        modules (list): A list of module paths to be bundled in the package.
        metadata (namedtuple): Metadata of the package.
        mainscript (bytes): The main script of the package. Must be in bytes
        (so we can ignore encoding).
    
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
            path_to_module: The path to the module. Must point to a file or a folder
            with a __init__.py file.
        
        Raises:
            PackageError: If a module could not be found at path_to_module.
        """
        # expand path first
        path_to_module = pathlib.Path(path_to_module).resolve().expanduser()

        if not utils.valid_module_path(path_to_module):
            raise PackageError(f"invalid module: '{path_to_module}'")

        self.modules.append(path_to_module)

    def build(self, bundle_meta: bool = True) -> bytes:
        """Compile the package (and optionally, the added modules) into a single
        ZipFile.
        
        Args:
            bundle_meta: Whether or not to export the package metadata as the ZipFile
            comment. True by default.
        
        Returns:
            The bytes of the ZipFile.
        """

        script_fname = self.metadata["name"] + ".py"
        # in-memory zipfile
        buffer = io.BytesIO(utils.EMPTY_ZIP_FILE)
        with zipfile.ZipFile(buffer, mode="w") as memzip:

            for module in self.modules:
                if module.is_dir():
                    utils.zipdir(module, memzip)
                elif module.is_file():
                    memzip.write(module)

            # Write main script
            memzip.writestr(script_fname, self.mainscript)

            if bundle_meta:
                memzip.comment = bytes(toml.dumps(self.metadata), encoding="utf8")

        return buffer.getbuffer()


class Repository(object):
    """A repository (bakery) for storing bao packages.
    
    A repository is a folder containing a zipfile for each package.
    A special file called 'BAKERY.toml' contains metadata of all packages in the
    repository.
    
    Args:
        name: The nickname of the repository.
    
    Attributes:
        name (str): The repo name.
        packages (dict): Map of packages in the repository to Package objects.
        metadata (readonly): Metadata of all packages in the repository.
    
    """

    def __init__(self, name: str):
        self.name = name
        self.packages = {}

    def add_package(self, package: Package) -> None:
        """Add a package to the repository.
        
        Args:
            package: The package. Must be a (subclass of) bao.abstract.Package.
        """

        if not isinstance(package, Package):
            raise RepositoryError("package must be a subclass of bao.abstract.Package")

        self.packages[package.metadata[name]] = package

    def del_package(self, package: str) -> None:
        """Remove a package from the repository.
        
        Args:
            package: The package to remove.
        """

        del self.packages[package]

    @property
    def metadata(self) -> dict:
        """Get metadata from all packages in the repository.
        
        Returns:
            The metadata.
        """

        meta = {}
        for pname, pobj in self.packages.items():
            meta[pname] = pobj.metadata
            # avoid duplication of "name" metadata
            del metadata[pname]["name"]

        return meta

    def build(self, path: str) -> None:
        """Compile a repository into a folder.
        
        Args:
            path: The path to the folder.
        
        Returns:
            None.
        
        Raises:
            PermissionError/IOError, if the folder is inaccessible.
        """

        metadata = {"nickname": self.name, "packages": self.metadata}

        # Output metadata
        with open("BAKERY.toml", mode="w") as f:
            toml.dump(metadata, f, indent=4)

        for package in self.packages:
            path = pathlib.Path(path) / package.metadata["name"] + ".zip"
            with path.open(mode="wb") as f:
                f.write(package.build())
