from io import StringIO

from scrapy.settings import Settings

from spider_feeder.parser.txt import Parser


def test_parse_txt_content():
    content = StringIO('http://url1.com\nhttp://url2.com\nhttp://url3.com')

    parser = Parser(Settings())
    urls = parser.parse(content)

    assert urls == ['http://url1.com', 'http://url2.com', 'http://url3.com']
