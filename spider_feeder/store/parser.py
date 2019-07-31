import json
from csv import DictReader


def parse_txt(fd, settings):
    return fd.read().splitlines()


def parse_csv(fd, settings):
    return [dict(x) for x in DictReader(fd)]


def parse_json(fd, settings):
    return json.load(fd)
