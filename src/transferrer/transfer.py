import os
import tempfile
from transferrer.download import download_shoot
from transferrer.make_zip import make_zip_from
from transferrer.upload import upload
import boto3

from common import shoot_number_to_folder_path
from make_zip import shoot_number_to_accession_id


MAX_SPACE_BYTES = 10240000000  # maximum setting for  Lambda Ephemeral Storage


def transfer_shoot(from_session, to_session, shoot_number, accession_number, max_batch_bytes=MAX_SPACE_BYTES / 2):
    accession_id = shoot_number_to_accession_id(accession_number, shoot_number)
    # /tmp needs space for both the images and their zipped form
    # The zip will be smaller, as the images are not well compressed,
    # but occupying half the available space is a nice, safe option
    root_dir = tempfile.TemporaryDirectory()
    tmpfolder = root_dir.name
    source_folder = os.path.join(tmpfolder, "source")
    target_folder = os.path.join(tmpfolder, "target")
    for files, suffix in download_shoot(from_session, shoot_number, source_folder, max_batch_bytes):
        upload(
            to_session,
            make_zip_from(files, source_folder, target_folder, accession_id, suffix)
        )
        root_dir.cleanup()


if __name__ == "__main__":
    import sys
    transfer_shoot(
        from_session=boto3.Session(profile_name=os.environ["AWS_SOURCE_PROFILE"]),
        to_session=boto3.Session(profile_name=os.environ["AWS_TARGET_PROFILE"]),
        shoot_number=sys.argv[1],
        accession_number="2754"
    )
