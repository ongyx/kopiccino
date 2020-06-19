"""Simple packaging test that bundles bao and this script into a bao package."""

import pathlib
import sys

import bao
from bao.abstract import Package
from bao.utils import autogen_metadata

__author__ = "Ong Yong Xin"
__license__ = "MIT"
__version__ = "1.0.0"

if len(sys.argv) < 2:
    print(f"usage: {__file__} </path/to/output/test/package>")
    sys.exit(1)

with open(__file__, mode="rb") as f:
    mainscript = f.read()

metadata = autogen_metadata(__file__)

pkg = Package(mainscript, metadata)
# add bao as a dependency (???)
pkg.add_module(pathlib.Path(bao.__file__).parent)
with open(pathlib.Path(sys.argv[1]).expanduser().resolve(), mode="wb") as f:
    f.write(pkg.build())

sys.exit(0)
