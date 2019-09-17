from io import StringIO
from urllib.request import urlopen


def open(url, encoding, settings):
    response = urlopen(url)
    return StringIO(response.read())
