from os import path
from urllib.parse import urlparse
import logging

from scrapy.utils.misc import load_object

from .base_store import BaseStore

logger = logging.getLogger(__name__)


class FileStore(BaseStore):
    '''Store class abstracting an input file.
    It can handle file stored in the local file system or in Amazon AWS S3.
    This is extensible by adding the given URI scheme to `SPIDERFEEDER_FILE_HANDLERS`.

    The file formats handled are txt, csv and json.
    If a new file format is required, it is just a matter of adding the file extension to
    `SPIDERFEEDER_FILE_HANDLERS`.
    For csv and json files, the URL is read from the field set in `SPIDERFEEDER_INPUT_FIELD`.

    The standard file encoding is _utf-8_, but it can be changed through `SPIDERFEEDER_INPUT_FILE_ENCODING`.
    '''

    FILE_HANDLERS = {
        '': 'spider_feeder.store.file_handler.local.open',
        'file': 'spider_feeder.store.file_handler.local.open',
        's3': 'spider_feeder.store.file_handler.s3.open',
        'http': 'spider_feeder.store.file_handler.http.open',
        'https': 'spider_feeder.store.file_handler.http.open',
    }

    FILE_PARSERS = {
        'txt': 'spider_feeder.store.parser.parse_txt',
        'csv': 'spider_feeder.store.parser.parse_csv',
        'json': 'spider_feeder.store.parser.parse_json',
    }

    def __init__(self, input_file_uri, settings):
        super().__init__(settings)
        self._input_file_uri = input_file_uri
        self._settings = settings
        self._input_file_encoding = settings.get('SPIDERFEEDER_INPUT_FILE_ENCODING', 'utf-8')
        self._input_format = settings.get('SPIDERFEEDER_INPUT_FORMAT', None)

        handlers = settings.getdict('SPIDERFEEDER_FILE_HANDLERS', {})
        self._handlers = dict(self.FILE_HANDLERS, **handlers)

        parsers = settings.getdict('SPIDERFEEDER_FILE_PARSERS', {})
        self._parsers = dict(self.FILE_PARSERS, **parsers)

    @property
    def _file_format(self):
        if self._input_format:
            return self._input_format

        (_, file_extension) = path.splitext(self._input_file_uri)
        return file_extension[1:]  # remove the "."

    def _open(self):
        parsed = urlparse(self._input_file_uri)
        logger.info(f'Opening file {self._input_file_uri} with scheme {parsed.scheme}.')
        open = load_object(self._handlers[parsed.scheme])
        return open(
            self._input_file_uri,
            encoding=self._input_file_encoding,
            settings=self._settings
        )

    def _parse(self, fd):
        file_format = self._file_format
        logger.info(f'Parsing file {self._input_file_uri} with format {file_format}.')
        parser = load_object(self._parsers[file_format])
        return parser(fd, self._settings)

    def read_input_items(self):
        with self._open() as fd:
            return self._parse(fd)
