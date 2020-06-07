# bao (包): script sharing made ez

_bao_ is a Python port of [package.swift](https://github.com/ColdGrub1384/LibTerm/Commands/builtins/package.swift), an inbuilt package manager for Libterm.

## Why yet another package manager?

[Pip](https://pypi.org/project/pip/) is the de-facto package manager for Python that has made distributing Python software reletively pain-free.
However, what if you wanted to share one-off scripts that simply does not justify the use of a full-blown package?

This is where _bao_ steps in. You simply put into a zip file:
- the main script (entrypoint, in pip terms),
- other modules (if it is a Pip package, see below)

or just place the files/directories into a folder and let _bao_ do the work for you, which yields a _bao_ package (a.k.a a bun).

## Installation

WIP

## Buns

From script to deployment:

```
mkdir helloworld && cd helloworld
echo 'print("Hello world!")' >> helloworld.py
bao bake .
ls  # helloworld.py  helloworld.zip  helloworld.toml
```
where `helloworld.zip` is the bun itself, and `helloworld.toml` is the bun metadata in [TOML}(https://en.wikipedia.org/wiki/TOML) format.
_bao_ parses the main script for the bun metadata, which should have the following attributes defined:

- `__doc__` (str): Docstring at the top of your script (bun description)
- `__author__`(str): The code authors.
- `__copyright__`(str): Usually, the first line of your license text. (You do include a license, do you?)
- `__license__`(str): The [SPDX](https://spdx.org/licenses/) identifer. If your code uses a custom license, put its short form here.
- `__version__`(str): The semantic version of the package (see [this](https://semver.org/).

From there, you can host the two files online and provide the URL of bun.toml to the enduser (bun.zip must be in the same path as bun.toml).

## Bakeries

A _bao_ repository is called a bakery.
To create a bakery, do:

```
mkdir testing && cd testing
bao bakery init .  # the name of the folder will be the repository nickname
...  # add your bun.zip and bun.toml here
bao bakery add *  # add all new buns
```

This creates a `.BAKERY.toml` file which contains a mapping of all buns to their metadata.
(Any .toml files from generating buns are then removed.)
If you add any more packages, run `bao bakery add *` again.

Alternatively, you can put your buns as folders (i.e unbaked), and _bao_ will create them automatically for you.

For backward compatibility, _bao_ can use the Github REST(v3) API to download packages if the .BAKERY.toml file is not present
(i.e in the [LibTerm-Packages](https://github.com/ColdGrub1384/LibTerm-Packages) repo).

## Libterm compatibility

On Libterm, _bao_ uses [userdefaults3](https://github.com/onyxware/userdefaults3) to modify `package.swift` configuration so any packages installed through `package.swift` is known to _bao_ and vice-versa.


