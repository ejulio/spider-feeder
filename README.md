# spider-feeder [Work in Progress]

This is a proof of concept to create an extension to load input urls to scrapy spiders.

Say there is an input file with the given URLs

```
# s3://urls.txt
https://url1.com
https://url2.com
https://url3.com
```

Then, you can configure the input in `settings.py`

```
# settings.py
EXTENSIONS = {
    'spider_feeder.loaders.StartUrlsLoader': 0
}

SPIDERFEEDER_INPUT_FILE = 's3://urls.txt'
```

The idea is to support various schemes: `s3`, `file`, `gs`, ...

Also, since it is a configuration, we can change it when running the spider.

`scrapy crawl myspider.com -s SPIDERFEEDER_INPUT_FILE="other_urls.txt"`

Also, if the standard file openers are not enough, you can write your custom ones as well.
After that, just register them in `SPIDERFEEDER_READERS`.

```
SPIDERFEEDER_READERS = {
    's3': 'myproject.my_custom_s3_reader.open'
}
```