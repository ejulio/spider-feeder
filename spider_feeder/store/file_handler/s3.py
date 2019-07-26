'''
This module handles `open()` for files stored in AWS S3.
'''
from io import StringIO
from urllib.parse import urlparse

from scrapy.utils.project import get_project_settings
from botocore.session import get_session


def open(blob_uri, encoding):
    parsed = urlparse(blob_uri)
    settings = get_project_settings()

    session = get_session()
    client = session.create_client(
        's3',
        aws_access_key_id=parsed.username or settings['SPIDERFEEDER_AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=parsed.password or settings['SPIDERFEEDER_AWS_SECRET_ACCESS_KEY'],
    )

    bucket_name = parsed.hostname
    key_name = parsed.path[1:]

    response = client.get_object(Bucket=bucket_name, Key=key_name, ResponseContentEncoding=encoding)
    content = response['Body'].read()
    return StringIO(content.decode(encoding))
