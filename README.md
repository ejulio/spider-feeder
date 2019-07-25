# spider-feeder
[![PyPI version](https://badge.fury.io/py/spider-feeder.svg)](https://badge.fury.io/py/spider-feeder)
[![Build Status](https://api.travis-ci.com/ejulio/spider-feeder.png)](https://api.travis-ci.com/ejulio/spider-feeder.png)

spider-feeder is a library to help loading inputs to scrapy spiders.

## Install

`pip install spider-feeder` or `pip install spider-feeder[s3]` to load files from AWS S3.

## Requirements

* If using `s3`, it requires `botocore`
* Otherwise, no requirements

## Usage (plain text)

Create a file `urls.txt` in your project with some urls (as in the example below).
```
https://url1.com
https://url2.com
https://url3.com
```

Then, in `settings.py`
```
EXTENSIONS = {
    'spider_feeder.loaders.StartUrlsLoader': 0
}

SPIDERFEEDER_INPUT_FILE = './urls.txt'
```

And run the spider `scrapy crawl myspider.com`

Once the URLs were loaded, the total count will be stored in a stats 
`spider_feeder/<spider.name>/url_count`.
This value is simply `len(spider.start_urls)`.

## Usage (csv/json)

Create a file `urls.csv` in your project with some urls (as in the example below).
```
id,input_url
1,https://url1.com
2,https://url2.com
3,https://url3.com
```

Then, in `settings.py`
```
EXTENSIONS = {
    'spider_feeder.loaders.StartUrlsLoader': 0
}

SPIDERFEEDER_INPUT_FILE = './urls.csv'
SPIDERFEEDER_INPUT_FIELD = 'input_url'
```

The same applies for `json`, just requiring to update the file extension to `.json` instead of `.csv`.
This means that the input file format is inferred from the given file extension.

## Settings

`SPIDERFEEDER_INPUT_FILE` is an URI to a file.
* If _scheme_ (`local`, `s3`) is not provided, it'll use `local`
* It can be formatted using spider attributes like `%(param)s` (similar to `FEED_URI` in scrapy)
* Supported schemes are: `''` or `file` for local files and `s3` for AWS S3 (requires `botocore`)
* When using `s3`, the URI must be formatted as `s3://key_id:secret_key@bucket/blob.txt`
* If `key_id` and `secret_key` are not provided in the URI, they can be provided by the following settings: `SPIDERFEEDER_AWS_ACCESS_KEY_ID` and `SPIDERFEEDER_AWS_SECRET_ACCESS_KEY`.

`SPIDERFEEDER_INPUT_FILE_ENCODING` sets the file encoding. DEFAULT = `'utf-8'`.

`SPIDERFEEDER_INPUT_FIELD` sets the url field when parsing `json` or `csv` files.

`SPIDERFEEDER_FILE_HANDLERS` is a set of functions to be matched with the given file scheme.
You can set your own and it'll be merged with the default one.
The interface is just a plain function with two arguments `file_uri` and `encoding`.
```
# settings.py
SPIDERFEEDER_FILE_HANDLERS = {
    's3': 'myproject.my_custom_s3_reader.open'
}

# myproject.my_custom_s3_reader.py
def open(file_uri, encoding):
    # my code here
    pass
```

`SPIDERFEEDER_FILE_PARSERS` is a set of parsers to be matched with the given file extension.
You can set your own and it'll be merged with the default one.
The interface is class with `__init__(settings: scrapy.Settings)` and `parse(fd: file object) -> List[str]` method.
```
# settings.py
SPIDERFEEDER_FILE_PARSERS = {
    's3': 'myproject.my_custom_parser.CustomParser'
}

# myproject.my_custom_parser.py
class CustomParser:
    def __init__(self, settings):
        pass
    
    def parse(self, fd):
        # some parsing strategy
        return ['url1', 'url2']
```