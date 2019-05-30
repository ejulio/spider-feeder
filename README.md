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

Once the URLs were loaded, the total count will be stored in a stats 
`spider_feeder/<spider.name>/url_count`.
This value is simply `len(spider.start_urls)`.

## Settings

`SPIDERFEEDER_INPUT_FILE` is an URI to a file.
* If _scheme_ (`local`, `s3`) is not provided, it'll use `local`
* It can be formatted using spider attributes like `%(param)s` (similar to `FEED_URI` in scrapy)
* Supported schemes are: `''` or `file` for local files and `s3` for AWS S3 (requires `botocore`)

`SPIDERFEEDER_INPUT_FILE_ENCODING` sets the file encoding. DEFAULT = `'utf-8'`.

`SPIDERFEEDER_FILE_HANDLERS` is a set of functions to be matched with the given file scheme.
You can set your own and it'll be merged with the default one.
The interface is just a plain function with two arguments `file_uri` and `encoding`.
```
# settings.py
SPIDERFEEDER_READERS = {
    's3': 'myproject.my_custom_s3_reader.open'
}

# myproject.my_custom_s3_reader.py
def open(file_uri, encoding):
    # my code here
    pass
```