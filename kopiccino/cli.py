# coding: utf-8
"""kopiccino: pure-Python port of LibTerm's 'package.swift' command.
"""

import argparse
import pathlib
import sys

from .abstract import Package, Repository
from .utils import autogen_metadata

# subcommand tree
# TODO: Use set_defaults(func=...) to delegate automatically to helper functions
COMMANDS = {
    "top-level": {"--verbose": {"action": "count", "default": 0}},
    "install": {
        "help": "install a package",
        "args": {
            "package": {
                "action": "store",
                "nargs": "+",
                "help": "the package name or direct URL, i.e 'repo_name/package_name', 'https://example.server/path/to/package'",
            }
        },
    },
    "uninstall": {
        "help": "uninstall a package",
        "args": {
            "package": {"action": "store", "nargs": "+", "help": "the package name"}
        },
    },
    "repo": {
        "help": "manage repositories",
        "subcommands": {
            "add": {
                "help": "add a repository",
                "args": {
                    "url": {
                        "action": "store",
                        "nargs": "+",
                        "help": "the repository url",
                    }
                },
            },
            "del": {
                "help": "remove a repository",
                "args": {
                    "nickname": {
                        "action": "store",
                        "help": "the repository nickname (list all with 'kopiccino repo list')",
                    }
                },
            },
            "list": {
                "help": "list all repositories",
                "args": {
                    "nickname": {
                        "action": "store",
                        "nargs": "?",
                        "default": "",
                        "help": "the repository nickname, for more specific info.",
                    }
                },
            },
        },
    },
}


def make_package(mainscript_path, module_paths):
    with open(mainscript_path, mode="rb") as f:
        mainscript = f.read()

    pkg = Package(mainscript_path, autogen_metadata(mainscript_path))
    for mod in module_paths:
        pkg.add_module(mod)

    return pkg


def main(argv=sys.argv[1:]) -> int:

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog="kopiccino",
    )

    if len(argv) == 0:
        parser.print_help()
        return 1

    args = parser.parse_args(argv)

    return 0


sys.exit(main())
