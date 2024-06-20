import os
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import boto3

from transferrer.common import should_download_file, shoot_number_to_folder_path, get_source_bucket

logger = logging.getLogger(__name__)

# This variable governs the degree of parallelism to use when downloading files.
# The correct number is to be discovered by experimentation
THREADS = 10


def download_shoot(session: boto3.session.Session, shoot_number, local_dir):
    # Allowing enough connections for each thread to have two of them
    # prevents the `urllib3.connectionpool:Connection pool is full` warning
    # and allows for better connection reuse.
    download_shoot_folder(get_source_bucket(session, max_connections=THREADS * 2), shoot_number, local_dir)


def download_shoot_folder(bucket, shoot_number, local_dir):
    download_s3_folder(bucket, shoot_number_to_folder_path(shoot_number), local_dir)


def download_s3_folder(bucket, s3_folder: str, local_dir: str):
    """
    Download the relevant content from an s3 folder to local_dir.

    This function runs parallel reads according to the AWS guidance here:
    https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/run-parallel-reads-of-s3-objects-by-using-python-in-an-aws-lambda-function.html

    """
    os.makedirs(local_dir, exist_ok=True)
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for key in executor.map(
            partial(download_s3_file, local_dir=local_dir, s3_folder=s3_folder),
            (obj for obj in bucket.objects.filter(Prefix=s3_folder) if should_download_file(obj.key))
        ):
            logger.info(f"downloaded\t{key}")


def download_s3_file(object_summary, *, local_dir: str, s3_folder: str):
    logger.info(f"downloading\t{object_summary.key}")
    target = os.path.join(local_dir, os.path.relpath(object_summary.key, s3_folder))
    object_summary.Object().download_file(target)
    return object_summary.key


if __name__ == "__main__":
    import sys
    shoot_number = sys.argv[1]
    download_folder = os.path.join("download", shoot_number)
    download_shoot(boto3.Session(), sys.argv[1], download_folder)
