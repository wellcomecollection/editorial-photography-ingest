import os
import pytest
import pyfakefs
from transferrer.download import download_shoot_folder
HERE = os.path.dirname(os.path.abspath(__file__))


def test_ignores_metadata_files(available_shoot_bucket, fs):
    download_shoot_folder(available_shoot_bucket, "PITEST", "downloaded")
    downloaded_files = os.listdir("downloaded")
    assert sorted(downloaded_files) == ['PI_TEST_001.tif', 'PI_TEST_002.tif']


def test_downloads_restored_bucket(glacier_shoot_bucket, fs):
    with pytest.raises(Exception):
        download_shoot_folder(glacier_shoot_bucket, "PITEST", "downloaded")
    downloaded_files = os.listdir("downloaded")
    assert sorted(downloaded_files) == []


def test_fails_partially_unrestored_bucket(available_shoot_bucket, fs):
    unrestored_file = os.path.join(HERE, "resources", "PI_TEST", "PI_TEST_003.tif")
    fs.create_file(unrestored_file)
    available_shoot_bucket.upload_file(
        unrestored_file, "ST/PI_TEST/PI_TEST_003.tif",
                       ExtraArgs={'StorageClass': 'GLACIER'})

    with pytest.raises(Exception):
        download_shoot_folder(available_shoot_bucket, "PITEST", "downloaded")
    downloaded_files = os.listdir("downloaded")
