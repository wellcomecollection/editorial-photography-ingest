import os

from transferrer.common import should_download_file, shoot_number_to_folder_path, get_source_bucket


def restore_s3_folder(bucket, s3_folder: str, days_to_keep=1):
    print(s3_folder)
    for obj in bucket.objects.filter(Prefix=s3_folder):
        print(obj.key)
        if should_download_file(obj.key):
            print(obj.restore_object(
                RestoreRequest={
                    'Days': days_to_keep,
                    'GlacierJobParameters': {
                        'Tier': 'Bulk'
                    }
                }
            ))


def restore_shoot_folder(bucket, shoot_number):
    restore_s3_folder(bucket, shoot_number_to_folder_path(shoot_number))


def restore_shoot_folders(shoot_numbers):
    bucket = get_source_bucket()
    for shoot_number in shoot_numbers:
        print(f"restoring {shoot_number}")
        restore_shoot_folder(bucket, shoot_number)


def main():
    import sys
    restore_shoot_folders(sys.argv[1:])


if __name__ == "__main__":
    main()
