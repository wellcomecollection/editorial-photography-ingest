import os
import moto
import boto3
import pytest
import pyfakefs
from transferrer.download import get_bucket, download_shoot_folder

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


def populate_bucket(bucket):
    bucket.upload_file(os.path.join(HERE, "resources", "PI_TEST", "PI_TEST_001.tif"), "ST/PI_TEST/PI_TEST_001.tif")
    bucket.upload_file(os.path.join(HERE, "resources", "PI_TEST", "PI_TEST_002.tif"), "ST/PI_TEST/PI_TEST_002.tif")
    bucket.upload_file(os.path.join(HERE, "resources", "PI_TEST", "PI_TEST.xml"), "ST/PI_TEST/PI_TEST.xml")
    bucket.upload_file(os.path.join(HERE, "resources", "PI_TEST", "shoot.csv"), "ST/PI_TEST/shoot.csv")
    return bucket


@pytest.fixture
def bucket_with_shoot(empty_bucket):
    return populate_bucket(get_bucket())


def test_ignores_metatdata_files(bucket_with_shoot, fs):
    b = bucket_with_shoot
    download_shoot_folder(b, "PITEST", "downloaded")
    downloaded_files = os.listdir("downloaded")
    assert sorted(downloaded_files) == ['PI_TEST_001.tif', 'PI_TEST_002.tif']
