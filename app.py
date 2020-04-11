import os
import stat
import time
import math
from urllib.parse import unquote

from flask import Flask
from flask import render_template
from flask import send_file

app = Flask(__name__)

ROOT_FOLDER = os.environ.get("DIRLISTER_TARGET", "/")

@app.template_filter('strftime')
def _jinja2_filter_datetime(epoch):
    human_time = time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(epoch))
    return human_time

@app.template_filter('data')
def _jinja2_filter_convert_size(size_bytes):
    width = 7
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

    if size_bytes != 0:

        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 1)

    else:
        s = 0
        i = 0

    string = f"{s: {width}} {size_name[i]}"
    padded_html_string = string.replace(" ", "&nbsp;")
    return padded_html_string

def _file_properties(filepath, item):
    #Opening the file and getting metadata
    fd = os.open(filepath, os.O_RDONLY)
    sbuf = os.fstat(fd)
    os.close(fd)

    fileProperties             = {}
    fileProperties["filepath"] = filepath
    fileProperties["name"]     = item
    fileProperties['type']     = stat.S_IFMT(sbuf.st_mode)
    fileProperties['mode']     = stat.S_IMODE(sbuf.st_mode)
    fileProperties['mtime']    = sbuf.st_mtime
    fileProperties['size']     = sbuf.st_size

    return fileProperties

def _folder_properties(fullpath, item):
    folderProperties             = {}
    folderProperties["relative"] = fullpath.replace(ROOT_FOLDER, "", 1)
    folderProperties["name"]     = item

    return folderProperties

def _hidden_item(item):
    if item.startswith("."):
        return True

    elif item.startswith("$"):
        return True

    else:
        return False

def _get_metadata(cwd):
    # Get information about files and folders
    files = []
    dirs = []

    for item in os.listdir(cwd):

        # Do not display hidden files and folders
        if _hidden_item(item):
            continue

        fullpath = os.path.join(cwd, item)

        if os.path.isdir(fullpath):
            folder = _folder_properties(fullpath, item)
            dirs.append(folder)

        if os.path.isfile(fullpath):
            file_props = _file_properties(fullpath, item)
            files.append(file_props)

    return dirs, files


@app.route('/')
def browse():

    # List files and folders for the root directory
    dirs, files = _get_metadata(ROOT_FOLDER)
    return render_template('browse.html', cwd=ROOT_FOLDER, dirs=dirs, files=files)

@app.route('/b/<path:newPath>')
def browser(newPath):
    path = unquote(newPath)

    # Download a file
    fullpath = os.path.sep+path
    if os.path.isfile(fullpath):
        return send_file(fullpath, as_attachment=True)

    # List files and folders
    fullpath = os.path.join(ROOT_FOLDER, path)
    dirs, files = _get_metadata(fullpath)

    return render_template('browse.html', cwd=path, dirs=dirs, files=files)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
