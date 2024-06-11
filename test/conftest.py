import os.path
import moto
import boto3
import pytest

from transferrer.common import get_source_bucket

HERE = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def empty_bucket():
    moto_fake = moto.mock_aws()
    try:
        moto_fake.start()
        conn = boto3.resource('s3', region_name="eu-west-1",)
        conn.create_bucket(CreateBucketConfiguration={
            'LocationConstraint': 'eu-west-1'
        }, Bucket="wellcomecollection-editorial-photography")
        yield conn
    finally:
        moto_fake.stop()


@pytest.fixture
def available_shoot_bucket(empty_bucket):
    return populate_bucket(get_source_bucket(), extra_args={})


@pytest.fixture
def glacier_shoot_bucket(empty_bucket):
    return populate_bucket(get_source_bucket(), extra_args={'StorageClass': 'GLACIER'})


def populate_bucket(bucket, extra_args):
    bucket.upload_file(os.path.join(HERE, "resources", "PI_TEST", "PI_TEST_001.tif"), "ST/PI_TEST/PI_TEST_001.tif", ExtraArgs=extra_args)
    bucket.upload_file(os.path.join(HERE, "resources", "PI_TEST", "PI_TEST_002.tif"), "ST/PI_TEST/PI_TEST_002.tif", ExtraArgs=extra_args)
    bucket.upload_file(os.path.join(HERE, "resources", "PI_TEST", "PI_TEST.xml"), "ST/PI_TEST/PI_TEST.xml", ExtraArgs=extra_args)
    bucket.upload_file(os.path.join(HERE, "resources", "PI_TEST", "shoot.csv"), "ST/PI_TEST/shoot.csv", ExtraArgs=extra_args)
    return bucket
