import os
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial


from transferrer.common import should_download_file, shoot_number_to_folder_path, get_source_bucket

logger = logging.getLogger(__name__)
THREADS = 20


def download_s3_folder(bucket, s3_folder: str, local_dir: str):
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


def download_shoot_folder(bucket, shoot_number, local_dir):
    download_s3_folder(bucket, shoot_number_to_folder_path(shoot_number), local_dir)


def download_shoot(shoot_number, local_dir):
    download_shoot_folder(get_source_bucket(), shoot_number, local_dir)


if __name__ == "__main__":
    import sys
    shoot_number = sys.argv[1]
    download_folder = os.path.join("download", shoot_number)
    os.makedirs(download_folder, exist_ok=True)
    download_shoot_folder(get_source_bucket(THREADS), sys.argv[1], download_folder)