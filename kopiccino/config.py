# coding: utf8
"""Cross-platform config stuff.
Abstracts over all the platform diffrences, as well as providing an interface to
Libterm's UserDefaults data.

kopiccino configs are stored as TOML.
"""

import os
import pathlib
import platform
import plistlib

import toml
import userdefaults3
from .exceptions import ConfigError

USERHOME = userdefaults3.USERHOME
_IOS_SYSTEM_BIN = USERHOME / "Documents" / "bin"
CONFNAME = ".kopiccino.toml"

DARWIN = "Darwin" in platform.system()
LINUX = "Linux" in platform.system()

# used to find app platform
BUNDLE_IDS = {
    "Pythonista3": "com.omz-software.Pythonista3",
    "Pyto": "ch.marcela.ada.Pyto",
    "LibTerm": "ch.marcela.ada.LibTerm",
    "ashell": "AsheKube.app.a-Shell",
}

BINPATHS = {
    "posix": pathlib.Path("/usr") / "local" / "bin",
    "darwin": pathlib.Path("/usr") / "local" / "bin",
    "ios_Pythonista3": _IOS_SYSTEM_BIN,
    "ios_Pyto": _IOS_SYSTEM_BIN,
    "ios_LibTerm": (USERHOME / "Library" / "bin").resolve(),
    "ios_ashell": _IOS_SYSTEM_BIN,
}


def detect_platform() -> str:
    """Detect the underlying platform kopiccino is running on.
    
    Returns:
        The platform ID (can be one of the following):
        
        posix: *nix platforms and Linux/GNU
        darwin: macOS
        ios_APPNAME: where APPNAME can be 'Pythonista3', 'LibTerm', 'ashell' or 'pyto'
    """

    if LINUX:
        return "posix"

    elif DARWIN:

        # On iOS/macOS, check bundle identifier
        for app, bundle_id in BUNDLE_IDS.items():
            if userdefaults3.BUNDLE_ID == bundle_id:
                return f"ios_{app}"

        return "darwin"


PLATFORM = detect_platform()
BINPATH = BINPATHS[PLATFORM]


class LinuxUserDefaults(userdefaults3.BaseUserDefaults):
    """Shim for compatibility with UserDefaults on Linux systems.

    Args:
        path: The file to emulate as UserDefaults.
        backend: The object used for serialization (i.e json, toml, plistlib).
        Must support the following methods:
            .load()
            .loads()
            .dump()
            .dumps()
        Defaults to toml.
        
        Note that you have to handle any deserialization errors yourself.

    Attributes:
        data: The deserialized data.
    """

    def __init__(self, path: pathlib.Path, backend=toml):

        for method in ("load", "loads", "dump", "dumps"):
            try:
                _ = getattr(backend, method)
            except AttributeError:
                raise userdefaults3.UserDefaultsError(
                    f"backend does not have method {method}"
                )

        self._backend = backend

        try:
            with path.open(mode="rb") as f:
                self.data = backend.load(f)

        except FileNotFoundError:
            self.data = {}

        else:
            self._path = path

    def close(self):
        with self._path.open(mode="wb") as f:
            backend.dump(self.data, f)

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()


class Registry(object):
    """Public interface to kopiccino's package registry.
    
    Usage:
        with Registry() as reg:
            reg.add_package(metadata)
            reg.remove_package(name)
            # Changes are synced to the registry file at the end of the 'with' block.
    
    Attributes:
        files (dict): Registered packages as keys, with their installed files as
        values.
        
        meta (dict): Registered packages as keys, with their kopiccino
        metadata as values.

        config (dict): A dictionary-like interface to the registry.
    
    Raises:
        ConfigError, if the registry is inacessible/invalid.
    """

    def __init__(self):
        if DARWIN:
            self._config = userdefaults3.UserDefaults()

        elif LINUX:
            self._config = LinuxUserDefaults(USERHOME / CONFNAME)
