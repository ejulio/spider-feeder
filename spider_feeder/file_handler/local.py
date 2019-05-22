'''
This module handles `open()` for local files.
'''
import builtins


def open(file_uri, encoding):
    file_path = file_uri.replace('file://', '')
    return builtins.open(file_path, encoding=encoding)
