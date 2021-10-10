# pylint: disable=missing-module-docstring
import os
import re
import time
from urllib.parse import unquote

from flask import Flask
from flask import redirect
from flask import render_template
from flask import send_file

from dirlister.config import ROOT_FOLDER
from dirlister.config import load_filter
from dirlister.directory import byte_size_human_readable
from dirlister.directory import disk_usage
from dirlister.directory import metadata


filters = load_filter()

app = Flask(__name__)


@app.template_filter("pretty")
def _jinja2_pretty(name: str, dir_or_file: str = "dir") -> str:
    """The back button uses this to set the parent folder"""
    ext = ""
    if "file" in dir_or_file:
        name, ext = os.path.splitext(name)
    # Make everything lowercase for simple filtration
    name = name.lower()

    # Replace each filtered word with a space
    if filters:
        for i in filters["filters"]:
            name = name.replace(i.lower(), " ")

    # Replace each special character with a space
    name = re.sub(r"[^\w]", " ", name)
    return name.title().strip() + ext


@app.template_filter("previous")
def _jinja2_previous_folder(cwd: str) -> str:
    """The back button uses this to set the parent folder"""

    head, _ = os.path.split(cwd)
    return head


@app.template_filter("strftime")
def _jinja2_filter_datetime(epoch: int) -> str:
    """a files modified time is given in epoch and converted to human readable time"""

    if not epoch:
        return ""

    human_time = time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(epoch))
    return human_time


@app.template_filter("data")
def _jinja2_filter_convert_size(size_bytes: int) -> str:
    """Convert bytes to closest measure and uri encode it"""
    converted_bytes = byte_size_human_readable(size_bytes)
    padded_html_string = converted_bytes.replace(" ", "&nbsp;")

    return padded_html_string


@app.route("/")
def browse() -> str:
    """List files and folders for the root directory"""

    dirs, files, _ = metadata(ROOT_FOLDER)

    return render_template(
        "browse.html", cwd=ROOT_FOLDER, dirs=dirs, files=files, disk_usage=disk_usage()
    )


@app.route("/b/<path:new_path>")
def browser(new_path: str) -> str:
    """List files and folders of sub directory"""

    # convert url encoded characters back to normal
    path = unquote(new_path)
    fullpath = os.path.sep + path

    # Download a file
    if os.path.isfile(fullpath):
        return send_file(fullpath, as_attachment=True)

    # List files and folders
    fullpath = os.path.join(ROOT_FOLDER, path)
    dirs, files, error = metadata(fullpath)

    return render_template(
        "browse.html",
        cwd=path,
        dirs=dirs,
        files=files,
        error=error,
        disk_usage=disk_usage(),
    )


@app.errorhandler(404)  # type:ignore
def page_not_found(
    e: Exception,
):  # NOQA: ANN201 # pylint: disable=unused-argument disable=invalid-name
    """instead of display a 404 page, simply redirect back to root"""
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
