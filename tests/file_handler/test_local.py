from spider_feeder.file_handler import local


def test_open_local_file(mocker):
    mock = mocker.patch('spider_feeder.file_handler.local.builtins.open')
    local.open('/tmp/input_urls.txt', encoding='utf-8')
    mock.assert_called_once_with('/tmp/input_urls.txt', encoding='utf-8')


def test_open_local_file_with_scheme(mocker):
    mock = mocker.patch('spider_feeder.file_handler.local.builtins.open')
    local.open('file:///tmp/input_urls.txt', encoding='latin-1')
    mock.assert_called_once_with('/tmp/input_urls.txt', encoding='latin-1')
