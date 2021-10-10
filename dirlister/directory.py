# pylint: disable=missing-module-docstring
import math
import os
import shutil
import stat
from typing import Literal
from typing import Tuple
from typing import Union

from dirlister.config import ROOT_FOLDER


def _file_properties(filepath: str, item: str) -> dict:
    """Opens a file to read its various properties"""
    file_properties = {}
    file_properties["filepath"] = filepath
    file_properties["name"] = item
    file_properties["mode"] = 0
    file_properties["mtime"] = 0
    file_properties["size"] = 0

    try:
        with os.open(filepath, os.O_RDONLY) as filedata:
            sbuf = os.fstat(filedata)

        file_properties["mode"] = stat.S_IMODE(sbuf.st_mode)
        file_properties["mtime"] = sbuf.st_mtime
        file_properties["size"] = sbuf.st_size

    # Don't show files that can't be accessed and ignore the exception
    except PermissionError:
        pass

    finally:
        return file_properties  # pylint: disable=lost-exception


def _folder_properties(fullpath: str, item: str) -> dict:
    """set folder properties"""
    folder_properties = {}
    folder_properties["relative"] = fullpath.replace(ROOT_FOLDER, "", 1)
    folder_properties["name"] = item

    return folder_properties


def _hidden_item(item: str) -> bool:
    """files and folders that are unwanted"""
    if item.startswith("."):
        return True

    if item.startswith("$"):
        return True

    return False


def metadata(cwd: str) -> Tuple[list, list, Union[Literal[False], str]]:
    """Get information about files and folders"""
    files = []
    dirs = []
    directory = []
    error = False

    try:
        directory = os.listdir(cwd)
    except FileNotFoundError:
        error = f"File not found: {cwd}"
    except PermissionError:
        error = error = f"Permission denied: {cwd}"

    for item in directory:

        # Do not display hidden files and folders
        if _hidden_item(item):
            continue

        fullpath = os.path.join(cwd, item)

        if os.path.isdir(fullpath):
            dirs.append(_folder_properties(fullpath, item))

        if os.path.isfile(fullpath):
            files.append(_file_properties(fullpath, item))

    return dirs, files, error


def disk_usage() -> Tuple[str, str, str]:
    """Get the disk size, usage and space available and return as human readable measures"""
    disk = shutil.disk_usage(ROOT_FOLDER)

    total = byte_size_human_readable(disk.total, 1)
    used = byte_size_human_readable(disk.used, 1)
    free = byte_size_human_readable(disk.free, 1)

    return total, used, free


def byte_size_human_readable(size: int, width: int = 7) -> str:
    """
    convert bytes to closest measure
    width tells how much space to put between the number and the unit symbol
    """

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    megabyte = 1024

    if size != 0:
        i = int(math.floor(math.log(size, megabyte)))
        measure = math.pow(megabyte, i)
        result = round(size / measure, ndigits=1)

    else:
        result = 0
        i = 0

    return f"{result:{width}}{size_name[i]}"
