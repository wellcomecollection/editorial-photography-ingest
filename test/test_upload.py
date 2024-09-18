import pytest
import pyfakefs
import boto3
from transferrer.upload import upload
from moto import mock_aws

@mock_aws
def test_raises_on_missing_zip(moto_session, target_bucket, fs):
    with pytest.raises(FileNotFoundError):
        upload(moto_session, "missing.zip")

@mock_aws
def test_uploads_to_accessions_folder_in_bucket(moto_session, target_bucket, fs):
    fs.create_file("present.zip")
    upload(moto_session, "present.zip")
    assert [obj.key for obj in target_bucket.objects.all()] == ["born-digital-accessions/present.zip"]


