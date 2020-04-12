import os
import yaml

ROOT_FOLDER = os.environ.get("DIRLISTER_TARGET", "/")

def load_filter():
    ''' example filter.yaml:
        filters:
          - "[tag]"
          - "sausage"
          - 2020

        this filter would turn a file or directory that looks like this:
          "abc [tag] def sausage ghi 2020"
        into this:
          "abc def ghi"
    '''
    filters     = {}
    filter_file = ""

    if os.path.isfile("filter.yaml"):
        filter_file = "filter.yaml"
    else:
        file = open("filter.yaml", 'w+')
        file.write("filters:\n  - 'make a yaml list of things to filter from file and directory names'")
        file.close()

    if filter_file != "":
        with open(filter_file) as f:
            filter_raw = f.read()
        f.close()

        filters = yaml.safe_load(filter_raw)

    return filters
