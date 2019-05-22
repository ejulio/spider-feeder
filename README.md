# spider-feeder

spider-feeder is a library to help loading inputs to scrapy spiders.

## Install

`pip install -e git@github.com:ejulio/spider-feeder.git#egg=spider_feeder`

## Requirements

* If using `s3`, it requires `botocore`
* Otherwise, no requirements

## Usage

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

## Settings

`SPIDERFEEDER_INPUT_FILE` is an URI to a file.
* If not provided, it'll load a local file
* It can be formatted with spider attributes with `%(param)s` similar to `FEED_URI`
* Supported schemes are: `''` or `file` for local files and `s3` for AWS S3 (requires `botocore`)

`SPIDERFEEDER_INPUT_FILE_ENCODING` sets the file encoding. DEFAULT = `'utf-8'`.

`SPIDERFEEDER_FILE_HANDLERS` is a set of functions to be matched with the given file scheme.
You can set your own and it'll be merged with the default one.
```
SPIDERFEEDER_READERS = {
    's3': 'myproject.my_custom_s3_reader.open'
}
```