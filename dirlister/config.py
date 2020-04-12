import os
import yaml

ROOT_FOLDER = os.environ.get("DIRLISTER_TARGET", "/")


filters     = {}
filter_file = ""

if os.path.isfile("filter.yaml"):
    filter_file = "filter.yaml"

if filter_file != "":
    with open(filter_file) as f:
        filter_raw = f.read()
    f.close()

    filters = yaml.safe_load(filter_raw)
