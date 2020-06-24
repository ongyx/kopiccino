# coding: utf-8
"""kopiccino: pure-Python port of LibTerm's 'package.swift' command.

Features:
- External repo support.
- Backward-compatibility with the 'package' command. By accessing the UserDefaults plist file, packages installed by the 'package' command will appear in picaro, and vice versa.
- Package builder: Create a package out of a script automatically.

The backend for kopiccino data serialization is by default TOML.
"""

import argparse
import pathlib
import sys

from .abstract import Package, Repository
from .utils import autogen_metadata


def make_package(mainscript_path, module_paths):
    with open(mainscript_path, mode="rb") as f:
        mainscript = f.read()

    pkg = Package(mainscript_path, autogen_metadata(mainscript_path))
    for mod in module_paths:
        pkg.add_module(mod)

    return pkg


def main(argv=sys.argv[1:]) -> int:

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        prog="kopiccino"
    )
    subparser = parser.add_subparsers()

    parser_repo = subparser.add_parser("repo", help="manage repositories")
    parser_repo.add_argument(
        "action", action="store", choices=["add", "del", "list"], help="action to take"
    )
    parser_repo.add_argument(
        "nickname",
        action="store",
        default=None,
        nargs="?",
        type=str,
        help="the repository url/nickname",
    )
    
    if len(argv) == 0:
        parser.print_help()
        return 0
    
    args = parser.parse_args(argv)

    return 0


sys.exit(main())
