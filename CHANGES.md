# Changes

All notable changes to this project are here.
The top-most version is the newest one.

* **Added** means a new feature
* **Changed** means a new feature
* **Fixed** means a bug fix

Whenever possible, link the given PR with the feature/fix.

[Keep a Changelog](https://keepachangelog.com/en/1.0.0/), [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Development

### Added

* New setting `SPIDERFEEDER_INPUT_FORMAT` to set the file format or fall back to the file extension. [PR#18](https://github.com/ejulio/spider-feeder/pull/18)
* Fall back to `scrapy` AWS settings if not provided. [PR#20](https://github.com/ejulio/spider-feeder/pull/20)
* Fixed AWS settings set in Dash (Scrapy Cloud) UI. [PR#21](https://github.com/ejulio/spider-feeder/pull/21)

## 0.2.0 (2019-08-27)

### Added

* Support for `.csv` and `.json` input files [PR#8](https://github.com/ejulio/spider-feeder/pull/8)
* Support for Scrapinghub Collections [PR#11](https://github.com/ejulio/spider-feeder/pull/11)
* Support for loading urls and meta data through `StartUrlsAndMetaLoader` [PR #12](https://github.com/ejulio/spider-feeder/pull/12) and [PR #14](https://github.com/ejulio/spider-feeder/pull/14)

### Changed

* `SPIDERFEEDER_INPUT_FILE` setting to `SPIDERFEEDER_INPUT_URI`

## 0.1.0 (2019-05-30)

### Added

* Support for plain text files
