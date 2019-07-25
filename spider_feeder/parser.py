import json
from csv import DictReader

from scrapy.exceptions import NotConfigured


class TxtParser:

    def __init__(self, settings):
        pass

    def parse(self, fd):
        return fd.read().splitlines()


class CsvParser:

    def __init__(self, settings):
        pass

    def parse(self, fd):
        return list(DictReader(fd))


class JsonParser:
    def __init__(self, settings):
        pass

    def parse(self, fd):
        return json.load(fd)
