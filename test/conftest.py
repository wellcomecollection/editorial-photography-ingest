import os.path
from contextlib import contextmanager
import moto
import boto3
import pytest

from transferrer.common import get_source_bucket

HERE = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture
def moto_s3():
    moto_fake = moto.mock_aws()
    try:
        moto_fake.start()
        yield boto3.resource(service_name='s3', region_name="eu-west-1")
    finally:
        moto_fake.stop()


@pytest.fixture
def moto_session():
    moto_fake = moto.mock_aws()
    try:
        moto_fake.start()
        yield boto3
    finally:
        moto_fake.stop()



@pytest.fixture
def empty_bucket(moto_s3):
    @contextmanager
    def _empty_bucket(bucket_name):
        yield moto_s3.create_bucket(CreateBucketConfiguration={
            'LocationConstraint': 'eu-west-1'
        }, Bucket=bucket_name)
    yield _empty_bucket


@pytest.fixture
def available_shoot_bucket(empty_bucket):
    with empty_bucket("wellcomecollection-editorial-photography") as bucket:
        yield populate_bucket(bucket, extra_args={})


@pytest.fixture
def glacier_shoot_bucket(empty_bucket):
    with empty_bucket("wellcomecollection-editorial-photography") as bucket:
        yield populate_bucket(bucket, extra_args={'StorageClass': 'GLACIER'})


@pytest.fixture
def target_bucket(empty_bucket):
    with empty_bucket("wellcomecollection-archivematica-staging-transfer-source") as bucket:
        yield bucket


def populate_bucket(bucket, extra_args):
    bucket.upload_file(os.path.join(HERE, "resources", "PI_TEST", "PI_TEST_001.tif"), "ST/PI_TEST/PI_TEST_001.tif", ExtraArgs=extra_args)
    bucket.upload_file(os.path.join(HERE, "resources", "PI_TEST", "PI_TEST_002.tif"), "ST/PI_TEST/PI_TEST_002.tif", ExtraArgs=extra_args)
    bucket.upload_file(os.path.join(HERE, "resources", "PI_TEST", "PI_TEST.xml"), "ST/PI_TEST/PI_TEST.xml", ExtraArgs=extra_args)
    bucket.upload_file(os.path.join(HERE, "resources", "PI_TEST", "shoot.csv"), "ST/PI_TEST/shoot.csv", ExtraArgs=extra_args)
    return bucket
