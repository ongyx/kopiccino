# coding: utf8
"""kopiccino: pure-Python port of LibTerm's 'package.swift' command.
"""

import os
import sys

from .__about__ import (
    __author__,
    __copyright__,
    __credits__,
    __license__,
    __version__,
    __maintainer__,
    __email__,
    __status__,
)

VERSION_REQUIRED = (3, 6)
ENABLE_PLATFORM_CHECK = False  # disable for debugging
IMPLICIT_NAMESPACE = True  # for testing

if not sys.version_info >= VERSION_REQUIRED:
    raise NotImplementedError(
        f"you must have at least Python {'.'.join(str(v) for v in VERSION_REQUIRED)}"
    )

if ENABLE_PLATFORM_CHECK:
    # use XPC service ID to check
    if "ch.marcela.ada.LibTerm" not in os.getenv("XPC_SERVICE_NAME"):
        raise NotImplementedError("Only LibTerm is supported now, sorry :(")

if IMPLICIT_NAMESPACE:
    from . import *

# don't muck up the namespace
del os, sys
