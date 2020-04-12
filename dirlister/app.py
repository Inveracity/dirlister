import os
import time
import math
import re
from urllib.parse import unquote

from flask import Flask
from flask import render_template
from flask import send_file
from flask import redirect

from dirlister.config import ROOT_FOLDER
from dirlister.config import filters
from dirlister.directory import metadata

app = Flask(__name__)


@app.template_filter('pretty')
def _jinja2_previous_folder(name):
    ''' The back button uses this to set the parent folder '''

    # Make everything lowercase for simple filtration
    name = name.lower()

    # Replace each filtered word with a space
    if filters:
        for i in filters["filters"]:
            name = name.replace(i.lower(), ' ')

    # Replace each special character with a space
    name = re.sub(r'[^\w]', ' ', name)
    return name.title()


@app.template_filter('previous')
def _jinja2_previous_folder(cwd):
    ''' The back button uses this to set the parent folder '''

    head, _ = os.path.split(cwd)
    return head


@app.template_filter('strftime')
def _jinja2_filter_datetime(epoch):
    ''' a files modified time is given in epoch and converted to human readable time '''

    if not epoch:
        return ""

    human_time = time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(epoch))
    return human_time


@app.template_filter('data')
def _jinja2_filter_convert_size(size_bytes):
    ''' Convert bytes to closest measure '''
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


@app.route('/')
def browse():
    ''' List files and folders for the root directory'''

    dirs, files, _ = metadata(ROOT_FOLDER)

    return render_template('browse.html', cwd=ROOT_FOLDER, dirs=dirs, files=files)


@app.route('/b/<path:newPath>')
def browser(newPath):
    ''' List files and folders of sub directory '''

    # convert url encoded characters back to normal
    path = unquote(newPath)
    fullpath = os.path.sep+path

    # Download a file
    if os.path.isfile(fullpath):
        return send_file(fullpath, as_attachment=True)

    # List files and folders
    fullpath = os.path.join(ROOT_FOLDER, path)
    dirs, files, error = metadata(fullpath)

    return render_template('browse.html', cwd=path, dirs=dirs, files=files, error=error)


@app.errorhandler(404)
def page_not_found(e):
    ''' instead of display a 404 page, simply redirect back to root '''
    return redirect("/")
