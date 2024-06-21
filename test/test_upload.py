import pytest
import pyfakefs
import boto3
from transferrer.upload import upload
from transferrer.upload import upload


def test_raises_on_missing_zip(moto_s3, target_bucket, fs):
    with pytest.raises(FileNotFoundError):
        upload(moto_s3, "missing.zip")


def test_uploads_to_accessions_folder_in_bucket(moto_s3, target_bucket, fs):
    fs.create_file("present.zip")
    upload(moto_s3, "present.zip")
    assert [obj.key for obj in target_bucket.objects.all()] == ["born-digital-accessions/present.zip"]


