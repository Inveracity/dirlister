import os
import stat

from dirlister.config import ROOT_FOLDER


def _file_properties(filepath, item):
    ''' Opens a file to read its various properties '''
    fileProperties             = {}
    fileProperties["filepath"] = filepath
    fileProperties["name"]     = item
    fileProperties['mode']     = 0
    fileProperties['mtime']    = 0
    fileProperties['size']     = 0

    try:
        fd = os.open(filepath, os.O_RDONLY)
        sbuf = os.fstat(fd)
        os.close(fd)
        fileProperties['mode']     = stat.S_IMODE(sbuf.st_mode)
        fileProperties['mtime']    = sbuf.st_mtime
        fileProperties['size']     = sbuf.st_size

    except PermissionError:
        pass

    finally:
        return fileProperties


def _folder_properties(fullpath, item):
    ''' set folder properties '''
    folderProperties             = {}
    folderProperties["relative"] = fullpath.replace(ROOT_FOLDER, "", 1)
    folderProperties["name"]     = item

    return folderProperties


def _hidden_item(item):
    ''' files and folders that are unwanted '''
    if item.startswith("."):
        return True

    elif item.startswith("$"):
        return True

    else:
        return False


def metadata(cwd):
    ''' Get information about files and folders '''
    files     = []
    dirs      = []
    directory = []
    error     = False

    try:
        directory = os.listdir(cwd)
    except FileNotFoundError:
        error = True

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
