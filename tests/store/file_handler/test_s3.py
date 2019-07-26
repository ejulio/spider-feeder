from datetime import datetime
from io import StringIO, BytesIO

import pytest
import botocore.session
from botocore.stub import Stubber
from botocore.response import StreamingBody

from spider_feeder.store.file_handler import s3


def get_object_response(content, encoding='utf-8'):
    stream = BytesIO(content.encode(encoding))
    return {
        'Body': StreamingBody(stream, len(content)),
        'DeleteMarker': False,
        'AcceptRanges': 'string',
        'Expiration': 'string',
        'Restore': 'string',
        'LastModified': datetime(2015, 1, 1),
        'ContentLength': 123,
        'ETag': 'string',
        'MissingMeta': 123,
        'VersionId': 'string',
        'CacheControl': 'string',
        'ContentDisposition': 'string',
        'ContentEncoding': 'string',
        'ContentLanguage': 'string',
        'ContentRange': 'string',
        'ContentType': 'string',
        'Expires': datetime(2015, 1, 1),
        'WebsiteRedirectLocation': 'string',
        'ServerSideEncryption': 'AES256',
        'Metadata': {'string': 'string'},
        'SSECustomerAlgorithm': 'string',
        'SSECustomerKeyMD5': 'string',
        'SSEKMSKeyId': 'string',
        'StorageClass': 'STANDARD',
        'RequestCharged': 'requester',
        'ReplicationStatus': 'COMPLETE',
        'PartsCount': 123,
        'TagCount': 123,
        'ObjectLockMode': 'GOVERNANCE',
        'ObjectLockRetainUntilDate': datetime(2015, 1, 1),
        'ObjectLockLegalHoldStatus': 'OFF'
    }


@pytest.fixture
def botocore_client():
    def _client(mocker):
        s3_client = botocore.session.get_session().create_client('s3')
        stubber = Stubber(s3_client)
        session_mock = mocker.Mock()
        session_mock.create_client.return_value = s3_client
        mocker.patch('spider_feeder.store.file_handler.s3.get_session', return_value=session_mock)
        return (stubber, session_mock)

    return _client


def test_open_s3_blob(botocore_client, mocker):
    (stubber, _) = botocore_client(mocker)
    with stubber:
        file_content = 'http://url1.com\nhttps://url1.com'
        response = get_object_response(file_content)
        expected_params = {
            'Bucket': 'bucket', 'Key': 'blob.txt', 'ResponseContentEncoding': 'utf-8'
        }
        stubber.add_response('get_object', response, expected_params)

        fd = s3.open('s3://bucket/blob.txt', encoding='utf-8')

        assert fd.read() == file_content
        assert isinstance(fd, StringIO)


def test_open_encoded_s3_blob(botocore_client, mocker):
    (stubber, _) = botocore_client(mocker)
    with stubber:
        file_content = 'http://url1.com\nhttps://url1.com\nhttp://vérystrangeurl.com'
        response = get_object_response(file_content, encoding='iso-8859-1')
        expected_params = {
            'Bucket': 'bucket', 'Key': 'blob.txt', 'ResponseContentEncoding': 'iso-8859-1'
        }
        stubber.add_response('get_object', response, expected_params)

        fd = s3.open('s3://bucket/blob.txt', encoding='iso-8859-1')

        assert fd.read() == file_content


def test_open_s3_blob_using_uri_credentials(botocore_client, mocker):
    (stubber, session_mock) = botocore_client(mocker)
    with stubber:
        file_content = 'http://url1.com\nhttps://url1.com'
        response = get_object_response(file_content)
        expected_params = {
            'Bucket': 'bucket', 'Key': 'blob.txt', 'ResponseContentEncoding': 'utf-8'
        }
        stubber.add_response('get_object', response, expected_params)

        s3.open('s3://key_id:secret@bucket/blob.txt', encoding='utf-8')

        session_mock.create_client.assert_called_once_with(
            's3',
            aws_access_key_id='key_id',
            aws_secret_access_key='secret',
        )


def test_open_s3_blob_using_project_credentials(botocore_client, mocker):
    (stubber, session_mock) = botocore_client(mocker)
    settings_mock = mocker.patch('spider_feeder.store.file_handler.s3.get_project_settings')
    settings_mock.return_value = {
        'SPIDERFEEDER_AWS_ACCESS_KEY_ID': 'key_id',
        'SPIDERFEEDER_AWS_SECRET_ACCESS_KEY': 'secret'
    }
    with stubber:
        file_content = 'http://url1.com\nhttps://url1.com'
        response = get_object_response(file_content)
        expected_params = {
            'Bucket': 'bucket', 'Key': 'blob.txt', 'ResponseContentEncoding': 'utf-8'
        }
        stubber.add_response('get_object', response, expected_params)

        s3.open('s3://bucket/blob.txt', encoding='utf-8')

        session_mock.create_client.assert_called_once_with(
            's3',
            aws_access_key_id='key_id',
            aws_secret_access_key='secret',
        )
