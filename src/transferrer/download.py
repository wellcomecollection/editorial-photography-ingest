import os

from transferrer.common import should_download_file, shoot_number_to_folder_path, get_source_bucket


def download_s3_folder(bucket, s3_folder: str, local_dir: str):
    os.makedirs(local_dir, exist_ok=True)

    downloadables = (obj for obj in bucket.objects.filter(Prefix=s3_folder) if should_download_file(obj.key))

    for obj in downloadables:
        target = os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        bucket.download_file(obj.key, target)


def download_shoot_folder(bucket, shoot_number, local_dir):
    download_s3_folder(bucket, shoot_number_to_folder_path(shoot_number), local_dir)


if __name__ == "__main__":
    import sys
    shoot_number = sys.argv[1]
    download_folder = os.path.join("download", shoot_number)
    download_shoot_folder(get_source_bucket(), sys.argv[1], download_folder)
