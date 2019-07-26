import json
from io import StringIO

import pytest
from scrapy.settings import Settings
from scrapy.exceptions import NotConfigured

from spider_feeder import parser


def test_parse_txt_content():
    content = StringIO('http://url1.com\nhttp://url2.com\nhttp://url3.com')

    urls = parser.parse_txt(content, Settings())

    assert urls == ['http://url1.com', 'http://url2.com', 'http://url3.com']


def test_parse_csv_content():
    content = StringIO('\n'.join([
        'id,url',
        '1,"http://url1.com"',
        '2,"http://url2.com"',
        '3,"http://url3.com"',
    ]))

    assert parser.parse_csv(content, Settings()) == [
        {'id': '1', 'url': 'http://url1.com'},
        {'id': '2', 'url': 'http://url2.com'},
        {'id': '3', 'url': 'http://url3.com'},
    ]


def test_parse_json_content():
    content = StringIO(json.dumps([
        {'id': 1, 'input_url': 'http://url1.com'},
        {'id': 2, 'input_url': 'http://url2.com'},
        {'id': 3, 'input_url': 'http://url3.com'},
    ]))

    assert parser.parse_json(content, Settings()) == [
        {'id': 1, 'input_url': 'http://url1.com'},
        {'id': 2, 'input_url': 'http://url2.com'},
        {'id': 3, 'input_url': 'http://url3.com'},
    ]
