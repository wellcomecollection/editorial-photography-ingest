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
