import logging
from botocore.exceptions import ClientError
from transferrer.common import should_download_file, shoot_number_to_folder_path, get_source_bucket

logger = logging.getLogger(__name__)


def restore_s3_folder(bucket, s3_folder: str, days_to_keep=1):
    logger.info(f"restoring folder {s3_folder}")
    for obj in bucket.objects.filter(Prefix=s3_folder):
        if should_download_file(obj.key):
            try:
                logger.info(obj.restore_object(
                    RestoreRequest={
                        'Days': days_to_keep,
                        'GlacierJobParameters': {
                            'Tier': 'Bulk'
                        }
                    }
                ))
            except ClientError as e:
                if "The operation is not valid for the object's storage class" in str(e):
                    logger.info(f"attempt to restore non-glacier object: {obj.key}")
                else:
                    raise
        else:
            logger.info(f"ignoring {obj.key}")

def restore_shoot_folder(bucket, shoot_number):
    restore_s3_folder(bucket, shoot_number_to_folder_path(shoot_number))


def restore_shoot_folders(shoot_numbers):
    bucket = get_source_bucket()
    for shoot_number in shoot_numbers:
        logger.info(f"restoring shoot {shoot_number}")
        restore_shoot_folder(bucket, shoot_number)


def main():
    import sys
    restore_shoot_folders(sys.argv[1:])


if __name__ == "__main__":
    main()
