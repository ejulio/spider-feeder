'''
This module handles `open()` for local files.
'''
import builtins
from urllib.parse import urlparse

def open(file_uri):
    file_path = file_uri.replace('file://', '')
    return builtins.open(file_path)
