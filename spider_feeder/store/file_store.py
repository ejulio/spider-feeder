from os import path
from urllib.parse import urlparse
import logging

from scrapy.utils.misc import load_object


logger = logging.getLogger(__name__)


class FileStore:

    FILE_HANDLERS = {
        '': 'spider_feeder.file_handler.local.open',
        'file': 'spider_feeder.file_handler.local.open',
        's3': 'spider_feeder.file_handler.s3.open',
    }

    FILE_PARSERS = {
        'txt': 'spider_feeder.parser.TxtParser',
        'csv': 'spider_feeder.parser.CsvParser',
        'json': 'spider_feeder.parser.JsonParser',
    }

    def __init__(self, input_file_uri, settings):
        self._input_file_uri = input_file_uri
        self._settings = settings
        self._file_encoding = settings.get('SPIDERFEEDER_INPUT_FILE_ENCODING', 'utf-8')
        self._input_field = settings.get('SPIDERFEEDER_INPUT_FIELD')

        handlers = settings.getdict('SPIDERFEEDER_FILE_HANDLERS', {})
        self._handlers = dict(self.FILE_HANDLERS, **handlers)

        parsers = settings.getdict('SPIDERFEEDER_FILE_PARSERS', {})
        self._parsers = dict(self.FILE_PARSERS, **parsers)

    def _open(self):
        parsed = urlparse(self._input_file_uri)
        logger.info(f'Opening file {self._input_file_uri} with scheme {parsed.scheme}.')
        open = load_object(self._handlers[parsed.scheme])
        return open(self._input_file_uri, encoding=self._file_encoding)

    def _parse(self, fd):
        (_, file_extension) = path.splitext(self._input_file_uri)
        file_extension = file_extension[1:]
        logger.info(f'Parsing file {self._input_file_uri} with format {file_extension}.')
        parser_cls = load_object(self._parsers[file_extension])
        parser = parser_cls(self._settings)
        return parser.parse(fd)

    def __iter__(self):
        for item in self._parse(self._open()):
            if self._input_field:
                if not isinstance(item, dict):
                    raise TypeError('Data is expected to be a dict when SPIDERFEEDER_INPUT_FIELD is set.')  # noqa

                yield (item[self._input_field], item)
            else:
                yield (item, {})
