# coding: utf8
"""Abstract representations of kopiccino packages and repositories.

A kopiccino package is a normal zipfile ('package.zip') plus a metadata file in TOML
format ('package.toml').

The zipfile must at least have a Python script with the same name as the package
itself ('package.py'). All other Python modules (and folders with __init__.py files)
are treated as internal modules. Anything else is ignored.

It is recommended that the internal module names start with the package name,
i.e {PACKAGE_NAME}_tests, to avoid namespace pollution. If the dependency is
avaliable from Pypi or installable through pip, use the 'pip_requires' key in the
package metadata instead.

A kopiccino repository is a folder which has one or more packages, with a central
index ('MANIFEST.toml') that tells kopiccino about the packages avaliable. The index
also
stores the metadata of all packages in the repository.

On creating a bakery from one or more packages, all .toml files are merged into the
'MANIFEST.toml' file.
"""

import io
import os
import pathlib
import requests
import shutil
import tempfile
import toml
from typing import Tuple
import zipfile

from . import utils
from .exceptions import PackageError, RepositoryError

log = utils.get_logger(__name__)

MANIFEST_FILENAME = "MANIFEST.toml"


class Package(object):
    """A bun (kopiccino package).
    If you subclass from this, make sure to call 'super().__init__(self, *args)'.
    
    Args:
        mainscript (default: b""): The main script of the package.

        metadata: Package metadata (see https://stackoverflow.com/a/1523456
            for a standard Python header format).
        
            See help(kopiccino.utils.autogen_metadata) for auto-extraction of metadata from
            a Python script.
        
            Mandatory fields:
        
            'name' (str) - Name of package
        
            'author' (list) - The author(s) who wrote the code
        
            'license' (str) - must be a SPDX ID
            (https://github.com/spdx/license-list-data/blob/master/json/licenses.json),
            or else it is treated as a custom license
        
            'version' (str) - semantic version of the package (https://semver.org)
        
            Optional fields:

            'doc' (str) - description, recommended
            'pypi_requires' (list) - a list of Pypi package dependencies
            
            Automatically generated fields:
            
            'modules' (list): A list of module paths in the ZipFile.
        
        data (default: utils.EMPTY_ZIP_FILE): The package data in ZipFile format.
            The package data will override the metadata and mainscript args
            (if it is not a empty ZipFile and override_existing=False).

        override_existing (default: False): Whether or not to ignore MANIFEST.toml in
            the package data and use the passed attributes instead (mainscript,
            metadata).
    
    Attributes:
        name (str): Name of the package.
        metadata (dict): Metadata of the package.
        buffer (io.BytesIO): The ZipFile containing the package metadata, as a buffer.
        unbundled (list): The list of unbundled modules.
    
    Raises:
        KeyError: If a required field in the metadata is not specified.
        PackageError: If the existing package metadata/mainscript could not be loaded
            from the ZipFile.
    """

    def __init__(
        self,
        mainscript: bytes = b"",
        metadata: dict = {},
        data: bytes = utils.EMPTY_ZIP_FILE,
        override_existing: bool = False,
    ):
        self.buffer = io.BytesIO(data)
        self.unbundled = []

        # try to parse the ZipFile data
        try:
            if override_existing:
                raise KeyError

            with zipfile.ZipFile(self.buffer).open(MANIFEST_FILENAME) as f:
                self.metadata = toml.load(f)

        except KeyError:
            log.info(f"Package has no {MANIFEST_FILENAME}, fallback to external metadata passed...")
            self.metadata = metadata
            utils._fill_defaults(self.metadata, utils.PACKAGE_ATTRIBUTES)
            # automatically generated attributes
            self.metadata["modules"] = []

        except toml.TomlDecodeError:
            raise PackageError(
                f"could not parse package manifest: {e} (Is your MANIFEST.toml corrupted?"
            )

        mainscript = self.name + ".py"
        try:
            if override_existing:
                raise KeyError

            with zipfile.ZipFile(self.buffer).open(mainscript) as f:
                self.mainscript = f.read()

        except KeyError:
            log.info(f"Package has no {mainscript}, fallback to external mainscript passed...")
            self.mainscript = mainscript
        
        log.debug(f"Finished initialising package '{self.name}'.")

    @property
    def name(self):
        return self.metadata["name"]

    @name.setter
    def name(self, value):
        self.metadata["name"] = value

    def add_module(self, path_to_module: pathlib.Path) -> None:
        """Bundle a module as a dependency in the package.
        
        Args:
            path_to_module: The path to the module. Must point to a file or a folder
            with a __init__.py file.
        
        Raises:
            PackageError: If a module could not be found at path_to_module.
        """

        if not utils.valid_module_path(path_to_module):
            raise PackageError(f"invalid module path: '{path_to_module}'")

        self.metadata["modules"].append(path_to_module.name)
        self.unbundled.append(path_to_module)

    def build(self, bundle_meta: bool = True) -> bytes:
        """Compile the package (and optionally, the added modules) into a single
        ZipFile.
        
        Args:
            bundle_meta: Whether or not to export the package metadata as the ZipFile
            comment. True by default.
        
        Returns:
            The bytes of the ZipFile.
        """

        mainscript = self.name + ".py"
        # in-memory zipfile
        with zipfile.ZipFile(self.buffer, mode="w") as memzip:

            for module in self.unbundled:

                # add unbundled modules
                if module.is_dir():
                    utils.zipdir(module, memzip)
                elif module.is_file():
                    memzip.write(module, arcname=module.name)
                
                log.info(f"Added module {module} to package data.")

            self.unbundled = []

            # Write main script
            memzip.writestr(mainscript, self.mainscript)

            if bundle_meta:
                log.debug("Bundling metadata...")
                memzip.writestr(
                    MANIFEST_FILENAME,
                    utils.TOML_CONF_HEADER + toml.dumps(self.metadata),
                )

        log.info(f"SUCCESS: built package {self.name}.")
        return self.buffer.getbuffer()


def get_online_package(
    url: str, metadata: dict, cli: bool = False
) -> Tuple[Package, requests.models.Response]:
    """Download a package from a URL.
    
    Args:
        url: The (direct) URL to download the package from. A GET request to this URL
            must return a ZipFile (in bytes) which may have bundled metadata as the
            comment; see help(kopiccino.abstract.Package.build)
        metadata: The metadata of the package (if the ZipFile downloaded does not
            have bundled metadata).
        cli: Whether or not to present a download bar using tqdm (by default, false).

    Returns:
        A two-tuple of (Package, raw_response) where Package is the data wrapped in a
            Package object, and raw_response is the return value of requests.get().

    Raises:
        PackageError, if the package could not be downloaded.
    """

    try:
        log.info(f"Downloading package from {url}...")
        data, response = utils.download_url(url, pbar=cli)
    except requests.exceptions.Timeout as err:
        raise PackageError(
            f"Could not download from {url}:"
            f"Server took too long to respond (>{utils.REQ_TIMEOUT} seconds)."
        ) from err
    except requests.exceptions.RequestException as err:
        raise PackageError(f"Could not download from {url}") from err
    
    log.info(f"SUCCESS: Downloaded package from {url}.")

    if metadata:
        return Package(metadata=metadata, data=data, override_existing=True), response

    else:
        return Package(metadata=metadata, data=data), response


class Repository(object):
    """A bakery (kopiccino repository) for storing buns.
    
    A repository is a folder containing a zipfile for each package.
    A special file called 'MANIFEST.toml' contains metadata of all packages in the
    repository.
    
    Args:
        name: The nickname of the repository.
    
    Attributes:
        name (str): The repo name.
        packages (dict): Map of packages in the repository to their names.
        metadata (readonly): Metadata of all packages in the repository.
    
    """

    def __init__(self, name: str):
        self.name = name
        self.packages = {}
        log.debug(f"Finished initalising repository '{self.name}'.")

    def add_package(self, package: Package) -> None:
        """Add a package to the repository.
        
        Args:
            package: The package. Must be a (subclass of) kopiccino.abstract.Package.
        """

        if not isinstance(package, Package):
            raise RepositoryError("package must be a subclass of kopiccino.abstract.Package")

        self.packages[package.name] = package
        log.info(f"Added package '{package.name}' to repository '{self.name}'.")

    def del_package(self, package_name: str) -> None:
        """Remove a package from the repository.
        
        Args:
            package_name: The package to remove.
        """

        del self.packages[package_name]
        log.info(f"Removed package '{package_name}' from repository '{self.name}'.")

    @property
    def metadata(self) -> list:
        return {k: v for (k, v.metadata) in self.packages.items()}

    def build(self, pth: pathlib.Path) -> None:
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
        with open(pth / MANIFEST_FILENAME, mode="w") as f:
            f.write(utils.TOML_CONF_HEADER)
            toml.dump(metadata, f)
        log.info(f"Generated metadata for repository '{self.name}'.")

        for package in self.packages:
            package_path = (pathlib.Path(pth) / package.name).with_suffix(".zip")
            with package_path.open(mode="wb") as f:
                f.write(package.build(bundle_meta=False))
        
        log.info(f"Built packages {', '.join([p.name for p in self.packages])} for repository {self.name}.")
