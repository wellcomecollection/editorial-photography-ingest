import logging
import os
import tempfile
from transferrer.download import download_shoot
from transferrer.make_zip import create_born_digital_zips
from transferrer.upload import upload
import boto3

def transfer_shoot(shoot_number, accession_number):
    with tempfile.TemporaryDirectory() as tmpfolder:
        source_folder = os.path.join(tmpfolder, "source")
        target_folder = os.path.join(tmpfolder, "target")
        download_shoot(shoot_number, source_folder)
        for zipfile in create_born_digital_zips(source_folder, target_folder, accession_number, shoot_number, 250):
            upload(zipfile)


if __name__ == "__main__":
    import sys
    transfer_shoot(boto3.Session(os.environ["AWS_TARGET_PROFILE"]).resource('s3'), sys.argv[1], "2754")
