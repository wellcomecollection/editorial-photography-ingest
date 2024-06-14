import os
import pytest
import pyfakefs
from transferrer.download import download_shoot_folder
from transferrer.restore import restore_shoot_folder


def test_ignores_metadata_files(glacier_shoot_bucket, fs):
    restore_shoot_folder(glacier_shoot_bucket, "PITEST")
    download_shoot_folder(glacier_shoot_bucket, "PITEST", "downloaded")
    downloaded_files = os.listdir("downloaded")
    assert sorted(downloaded_files) == ['PI_TEST_001.tif', 'PI_TEST_002.tif']


def test_idempotent(glacier_shoot_bucket, fs):
    # It doesn't matter if we request restoration multiple times
    restore_shoot_folder(glacier_shoot_bucket, "PITEST")
    restore_shoot_folder(glacier_shoot_bucket, "PITEST")
    download_shoot_folder(glacier_shoot_bucket, "PITEST", "downloaded")
    downloaded_files = os.listdir("downloaded")
    assert sorted(downloaded_files) == ['PI_TEST_001.tif', 'PI_TEST_002.tif']


def test_not_glacier_yet(glacier_shoot_bucket, fs):
    # It doesn't matter if some of the objects are in STANDARD storage
    non_glacier_file = "path/to/a/file"
    fs.create_file(non_glacier_file)
    glacier_shoot_bucket.upload_file(non_glacier_file, "ST/PI_TEST/PI_TEST_005.tif")
    restore_shoot_folder(glacier_shoot_bucket, "PITEST")
    download_shoot_folder(glacier_shoot_bucket, "PITEST", "downloaded")
    downloaded_files = os.listdir("downloaded")
    assert sorted(downloaded_files) == ['PI_TEST_001.tif', 'PI_TEST_002.tif', 'PI_TEST_005.tif']
