import os
from pathlib import Path
from textwrap import dedent

import yaml


ROOT_FOLDER = os.environ.get("DIRLISTER_TARGET", "/")


def load_filter() -> dict:
    """example filter.yaml:
    filters:
      - "[tag]"
      - "sausage"
      - 2020

    this filter would turn a file or directory that looks like this:
      "abc [tag] def sausage ghi 2020"
    into this:
      "abc def ghi"
    """
    filters = {}
    filter_file = ""

    filter_file = Path("filter.yaml")
    if not filter_file.exists():
        filter_file.write_text(
            dedent(
                """
                filters:
                - "make a yaml list of things to filter from files and directory names"
                """
            ).lstrip()
        )

    filter_raw = filter_file.read_text()

    filters = yaml.safe_load(filter_raw)

    return filters
