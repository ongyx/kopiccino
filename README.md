# kopiccino: script sharing made ez

_kopiccino_ is a Python port of [package.swift](https://github.com/ColdGrub1384/LibTerm/Commands/builtins/package.swift), an inbuilt package manager for Libterm.

## Why yet another package manager?

[Pip](https://pypi.org/project/pip/) is the de-facto package manager for Python that has made distributing Python software reletively pain-free.
However, what if you wanted to share one-off scripts that simply does not justify the use of a full-blown package?

This is where _kopiccino_ steps in. You simply put into a zip file:
- the main script (entrypoint, in pip terms),
- other modules (if it is a Pip package, see below)

or just place the files/directories into a folder and let _bao_ do the work for you, which yields a _bao_ package (a.k.a a bun).

## Installation

```
pip install kopiccino
```

A bootstrappable version for developemnt based on the latest Github commit is WIP.

## Packages

From script to deployment:

```
$ mkdir helloworld && cd helloworld
$ echo 'print("Hello world!")' >> helloworld.py
# add metadata to helloworld.py here
$ kopiccino pour .
$ ls
helloworld.py  helloworld.zip
```
where `helloworld.zip` is the package bundled with the metadata in [TOML](https://en.wikipedia.org/wiki/TOML) format.
_kopiccino_ parses the main script for the bun metadata, which should have the following attributes defined:

- `__doc__` (str): Docstring at the top of your script (package description)
- `__author__`(str): The code authors.
- `__license__`(str): The [SPDX](https://spdx.org/licenses/) identifer. If your code uses a custom license, put its short form here.
- `__version__`(str): The semantic version of the package (see [this](https://semver.org/).

From there, you can host the package online and provide the direct URL of to the enduser (bun.zip must be in the same path as bun.toml).

## Repositories

To create a local repository, do:

```
mkdir testing && cd testing
kopiccino local init .  # the name of the folder will be the repository nickname
# move your built/unbuilt packages here
kopiccino local register  # register all packages and build them, if needed
```

This creates a `MANIFEST.toml` file which contains a mapping of all packages to their
metadata. If you add any more packages, run `kopiccino local register` again.

Alternatively, you can put your packages as folders (i.e unbuilt), and _kopiccino_
will create them automatically for you.

For backward compatibility, _kopiccino_ can use the Github REST(v3) API to download
packages if the MANIFEST.toml file is not present (i.e in the [LibTerm-Packages](https://github.com/ColdGrub1384/LibTerm-Packages) repo).

## Libterm compatibility

On Libterm, _kopiccino_ uses [userdefaults3](https://github.com/onyxware/userdefaults3) to modify `package.swift` configuration so any packages installed through `package.swift` is known to _kopiccino_ and vice-versa.


