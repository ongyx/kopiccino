# coding: utf8
"""Helper functions, utilites, etc."""

import importlib
import shutil
import sys

from picaro.exceptions import PicaroError

PACKAGE_ATTRIBUTES = {
    "name": None,
    "author": None,
    "license": None,
    "copyright": None,
    "version": None,
    "doc": "",
    "maintainer": "",
    "email": "",
}


def _fill_defaults(data: dict, defaults: dict):
    """Fill in default values into a dictionary.
    
    Args:
        data: The dictionary to fill with default values.
        defaults: The default values. If a key in defaults is not found in data, the
        value of the key in defaults will be put into data.
        If the value of the key in defaults is None, a KeyError will be raised.
    """

    for key, value in defaults.items():
        result = data.get(key, None)
        if result is None:
            if value is not None:
                data[key] = value
            else:
                raise KeyError(f"field required: {key}")


def valid_module_path(path: str) -> bool:
    """Check if a path points to a vaild Python module
    (a .py file, or a directory with a __init__ file).
    The path must already exist in the filesystem.
    
    Args:
        path: The path to be checked.
    
    Returns:
        True if the path is a valid module, otherwise False.
    """

    path = pathlib.Path(path)

    if path.is_file() and path.name.endswith(".py"):
        # A python script
        return True

    else:
        initpath = path / "__init__.py"
        if path.is_dir() and initpath.is_file():
            return True

    return False


def copypath(src: str, dst: str) -> None:
    """Copy a path to a destination.
    
    Args:
        src: The path to copy. Must be an existing file/directory.
        dst: The path to copy to. Must be an directory.
    
    Returns:
        None.
    """

    src = pathlib.Path(src)

    if src.is_file():
        shutil.copy2(src, dir)

    elif src.is_dir():
        folder_dest = pathlib.Path(dst) / src.name
        shutil.copytree(src, folder_dest)

    else:
        raise shutil.Error("src is not a file or dir")


def autogen_metadata(module, module_path: str = None) -> dict:
    """Generate metadata for a Picaro package from a module.
    
    Args:
        module: The module/script to generate metadata from.
        module_path (optional): The path to the module, if it is not on sys.path already.
        Defaults to None.
    
    Returns:
        dict: The metadata generated.
    """

    metadata = {}
    old_sys_path = sys.path

    if module_path is not None:
        # add to the front of sys.path, because it could be overshadowed
        sys.path.insert(0, module_path)

    try:
        module = importlib.import_module(module)

    except ModuleNotFoundError:
        raise PicaroError("module does not exist: " + module)

    else:
        for attribute, default_value in PACKAGE_ATTRIBUTES.items():
            # header attributes start and end with underscores
            header_attr = f"__{attribute}__"

            try:
                metadata[attribute] = getattr(module, header_attr)

            except AttributeError:
                # check if attribute is non-default
                if default_value is None:
                    raise ValueError("metadata value not found: " + attribute)
                else:
                    metadata[attribute] = default_value

    finally:
        sys.path = old_sys_path

    return metadata
