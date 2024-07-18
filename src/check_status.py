import logging
import boto3
from transferrer.common import should_download_file, shoot_number_to_folder_path, get_source_bucket

logger = logging.getLogger(__name__)


def check_shoot_restore_status(bucket, shoot_number):
    check_folder_restore_status(bucket, shoot_number_to_folder_path(shoot_number))


def check_folder_restore_status(bucket, s3_folder: str):
    logger.info(s3_folder)
    for obj in bucket.objects.filter(Prefix=s3_folder,  OptionalObjectAttributes=[
        'RestoreStatus',
    ]):
        if should_download_file(obj.key):
            status = obj.restore_status
        else:
            status = "ignored"
        logger.info(f"{obj.key}\t{status}")


if __name__ == "__main__":
    import sys
    shoot_number = sys.argv[1]
    check_shoot_restore_status(get_source_bucket(boto3.Session()), sys.argv[1])
