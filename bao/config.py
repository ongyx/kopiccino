# coding: utf8
"""Cross-platform config stuff.
Abstracts over all the platform diffrences, as well as providing an interface to
Libterm's UserDefaults data.

bao configs are stored as TOML.
"""

import os
import pathlib
import platform
import plistlib

import userdefaults3
from .exceptions import ConfigError

USERHOME = userdefaults3.USERHOME
_IOS_SYSTEM_BIN = USERHOME / "Documents" / "bin"

# used to find app platform
BUNDLE_IDS = {
    "Pythonista3": "com.omz-software.Pythonista3",
    "Pyto": "ch.marcela.ada.Pyto",
    "LibTerm": "ch.marcela.ada.LibTerm",
    "ashell": "AsheKube.app.a-Shell",
}

BINPATHS = {
    "posix": pathlib.Path("/usr") / "local" / "bin",
    "ios_Pythonista3": _IOS_SYSTEM_BIN,
    "ios_Pyto": _IOS_SYSTEM_BIN,
    "ios_LibTerm": (USERHOME / "Library" / "bin").resolve(),
    "ios_ashell": _IOS_SYSTEM_BIN,
}


def detect_platform() -> str:
    """Detect the underlying platform bao is running on.
    
    Returns:
        The platform ID (can be one of the following):
        
        posix: *nix platforms and Linux/GNU
        darwin: macOS
        ios_APPNAME: where APPNAME can be 'Pythonista3', 'LibTerm', 'ashell' or 'pyto'
    """

    if platform.system() == "Linux":
        return "posix"

    elif platform.system() == "Darwin":

        # On iOS/macOS, check bundle identifier
        for app, bundle_id in BUNDLE_IDS.items():
            if userdefaults3.BUNDLE_ID == bundle_id:
                return f"ios_{app}"


PLATFORM = detect_platform()
BINPATH = BINPATHS[PLATFORM]


class Registry(object):
    """Public interface to bao's package registry.
    
    Usage:
        with Registry() as reg:
            reg.add_package(metadata)
            reg.remove_package(name)
            # Changes are synced to the registry file at the end of the 'with' block.
    
    Attributes:
        pkgfiles (dict): Registered packages as keys, with their installed files as
        values.
        
        pkgmeta (dict): Registered packages as keys, with their bao
        metadata as values.

        path (str): Filesystem location of the registry file.
    
    Raises:
        ConfigError, if the registry is inacessible.
    """

    def __init__(self):

        self.config = userdefaults3.UserDefaults()
