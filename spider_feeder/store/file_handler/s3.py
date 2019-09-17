'''
This module handles `open()` for files stored in AWS S3.
'''
from io import StringIO
from urllib.parse import urlparse
import logging

from botocore.session import get_session


logger = logging.getLogger(__name__)


def open(blob_uri, encoding, settings):
    parsed = urlparse(blob_uri)

    (aws_access_key_id, aws_secret_access_key) = _get_aws_keys(parsed, settings)
    session = get_session()
    client = session.create_client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    bucket_name = parsed.hostname
    key_name = parsed.path[1:]
    response = client.get_object(
        Bucket=bucket_name,
        Key=key_name,
        ResponseContentEncoding=encoding
    )
    content = response['Body'].read()
    return StringIO(content.decode(encoding))


def _get_aws_keys(parsed_uri, settings):
    aws_access_key_id = parsed_uri.username
    aws_secret_access_key = parsed_uri.password

    if not aws_access_key_id and not aws_secret_access_key:
        aws_access_key_id = settings.get('SPIDERFEEDER_AWS_ACCESS_KEY_ID')
        aws_secret_access_key = settings.get('SPIDERFEEDER_AWS_SECRET_ACCESS_KEY')

    if not aws_access_key_id and not aws_secret_access_key:
        aws_access_key_id = settings.get('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = settings.get('AWS_SECRET_ACCESS_KEY')

    if not aws_access_key_id and not aws_secret_access_key:
        logger.warning(
            'No AWS keys were set in the input URI or project settings. '
            'If that was intentional, make sure to have them set as environment variables.'
        )

    return (aws_access_key_id, aws_secret_access_key)
