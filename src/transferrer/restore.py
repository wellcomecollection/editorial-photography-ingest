import os

from transferrer.common import should_download_file, shoot_number_to_folder_path, get_source_bucket


def restore_s3_folder(bucket, s3_folder: str, days_to_keep=7):

    for obj in bucket.objects.filter(Prefix=s3_folder):
        if should_download_file(obj.key):
            obj.restore_object(
                RestoreRequest={
                    'Days': days_to_keep,
                    'GlacierJobParameters': {
                        'Tier': 'Bulk'
                    },
                    'Tier': 'Bulk'
                }
            )


def restore_shoot_folder(bucket, shoot_number):
    restore_s3_folder(bucket, shoot_number_to_folder_path(shoot_number))


def restore_shoot_folders(shoot_numbers):
    for shoot_number in shoot_numbers:
        restore_shoot_folder(get_source_bucket(), shoot_number)


def main():
    import sys
    shoot_number = sys.argv[1]
    restore_shoot_folders(sys.argv[1:])


if __name__ == "__main__":
    main()
