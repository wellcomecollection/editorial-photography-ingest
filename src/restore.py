import logging
from functools import partial
import boto3
from botocore.exceptions import ClientError
from concurrent.futures import ThreadPoolExecutor

from transferrer.common import should_download_file, shoot_number_to_folder_path, get_source_bucket
logger = logging.getLogger(__name__)

# This variable governs the degree of parallelism to use when restoring folders.
# The correct number is to be discovered by experimentation
THREADS = 10


def restore_s3_folder(bucket, s3_folder: str, days_to_keep=7):
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for key in executor.map(
            partial(restore_file, days_to_keep=days_to_keep),
            (obj for obj in bucket.objects.filter(Prefix=s3_folder) if should_download_file(obj.key))
        ):
            logger.info(f"restore request sent: \t{key}")



def restore_file(obj, *, days_to_keep):
    try:
        obj.restore_object(
            RestoreRequest={
                'Days': days_to_keep,
                'GlacierJobParameters': {
                    'Tier': 'Bulk'
                }
            }
        )
        return obj.key
    except ClientError as e:
        if "The operation is not valid for the object's storage class" in str(e):
            logger.info(f"attempt to restore non-glacier object: {obj.key}")
        elif "RestoreAlreadyInProgress" in str(e):
            logger.info(f"redundant attempt to restore object: {obj.key}")
        else:
            raise

def restore_shoot_folder(bucket, shoot_number):
    restore_s3_folder(bucket, shoot_number_to_folder_path(shoot_number))


def restore_shoot_folders(shoot_numbers):
    bucket = get_source_bucket(boto3.Session())
    for shoot_number in (n.strip() for n in shoot_numbers):
        logger.info(f"restoring shoot {shoot_number}")
        restore_shoot_folder(bucket, shoot_number)


def main():
    import sys
    restore_shoot_folders(sys.stdin.readlines())


if __name__ == "__main__":
    main()
