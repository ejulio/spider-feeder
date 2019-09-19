from spider_feeder.store.file_handler import http


def test_open_http_file(mocker):
    urlopen_mock = mocker.patch('spider_feeder.store.file_handler.http.urlopen')
    urlopen_mock().read.return_value = 'FILE CONTENT'

    url = 'https://someurl.com/index?qs=1'
    fd = http.open(url, encoding='utf-8', settings=None)

    urlopen_mock.assert_called_with(url)
    assert fd.read() == 'FILE CONTENT'
