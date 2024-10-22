import itertools
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import boto3

from transferrer.common import should_download_file, shoot_number_to_folder_path, get_source_bucket
from transferrer.batching import batch_by_total

logger = logging.getLogger(__name__)

# This variable governs the degree of parallelism to use when downloading files.
# The correct number is to be discovered by experimentation
THREADS = 20


def get_shoot_batches(bucket, s3_folder, max_batch_bytes):
    """
    A shoot has a maximum size defined by the space available on the device running
    the transfer, and the total number of files that Archivematica can tolerate
    in a single upload.
    This examines the ObjectSummaries corresponding to the photos in the shoot
    and divides the shoot into batches that fit within the constraints.
    These can then be downloaded, zipped, and transferred.

    Given that this is designed to run on Lambda, operating on high-quality images,
    the limit for ephemeral storage there will be encountered before the limit on
    the number of files in an upload, so that constraint is not applied here.
    """
    return batch_by_total(
        # Sort the objects by key for consistency.  This way, if this ends up with multiple batches,
        # Then regardless of how many times you run it, the batches will be the same as the last time.
        entries=sorted(list_folder_objects(bucket, s3_folder), key=lambda obj: obj.key),
        maximum=max_batch_bytes,
        key=lambda obj: obj.size
    )


def list_folder_objects(bucket, s3_folder):
    return (obj for obj in bucket.objects.filter(Prefix=s3_folder) if should_download_file(obj.key))


def download_shoot(session: boto3.session.Session, shoot_number, local_dir, max_batch_bytes, ignore_suffixes):
    # Allowing enough connections for each thread to have two of them
    # prevents the `urllib3.connectionpool:Connection pool is full` warning
    # and allows for better connection reuse.
    return download_shoot_folder(get_source_bucket(session, max_connections=THREADS * 5), shoot_number, local_dir, max_batch_bytes, ignore)


def download_shoot_folder(bucket, shoot_number, local_dir, max_batch_bytes, ignore_suffixes):
    return download_s3_folder(bucket, shoot_number_to_folder_path(shoot_number), local_dir, max_batch_bytes, ignore_suffixes)


def download_s3_folder(bucket, s3_folder: str, local_dir: str, max_batch_bytes: int, ignore_suffixes):
    """
    Download the relevant content from an s3 folder to local_dir.

    This function runs parallel reads according to the AWS guidance here:
    https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/run-parallel-reads-of-s3-objects-by-using-python-in-an-aws-lambda-function.html

    """
    image_batches = list(get_shoot_batches(bucket, s3_folder, max_batch_bytes))
    use_suffix = (len(image_batches) > 1)
    suffix = ""
    for ix, batch in enumerate(image_batches, 1):
        os.makedirs(local_dir, exist_ok=True)
        if use_suffix:
            suffix = f"_{ix:03d}"
        if suffix in ignore_suffixes:
            logger.info(f"{suffix} already on target, ignoring")
        else:
            with ThreadPoolExecutor(max_workers=THREADS) as executor:
                files = list(executor.map(
                    partial(download_s3_file, local_dir=local_dir, s3_folder=s3_folder),
                    batch
                ))
            yield files, suffix


def download_s3_file(object_summary, *, local_dir: str, s3_folder: str):
    logger.info(f"downloading\t{object_summary.key}")
    filename = os.path.relpath(object_summary.key, s3_folder)
    target = os.path.join(local_dir, os.path.relpath(object_summary.key, s3_folder))
    object_summary.Object().download_file(target)
    return filename


def main(shoot_number):
    download_folder = os.path.join("download", shoot_number)
    for batch in download_shoot(boto3.Session(), sys.argv[1], download_folder):
        print(batch)

if __name__ == "__main__":
    import sys
    main(sys.argv[1])

