import boto3
import os
from make_zip import discard_file


def shoot_number_to_folder_path(shoot_number):
    """
    A shoot number consists of two letters followed by six digits
    >>> shoot_number = "CP000159"

    The files are arranged in folders according to the last two number of the shoot,
    and then by shoot number - In the folder name, the alphabetic prefix is separated from the
    rest of the number by an underscore

    >>> shoot_number_to_folder_path("CP000159")
    '59/CP_000159'
    """
    parent_folder = shoot_number[-2:]
    folder_name = "_".join([shoot_number[:2], shoot_number[2:]])
    return "/".join([parent_folder, folder_name])


def should_download_file(key):
    return (
        # you can't download a folder
        key[-1] != '/'
        and
        # don't download something you are going to throw away
        not discard_file(key)
    )


def download_s3_folder(bucket, s3_folder, local_dir):
    os.makedirs(local_dir, exist_ok=True)
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        if should_download_file(obj.key):
            bucket.download_file(obj.key, target)


def download_shoot_folder(bucket, shoot_number, local_dir):
    download_s3_folder(bucket, shoot_number_to_folder_path(shoot_number), local_dir)


def get_bucket():
    session = boto3.Session()
    S3 = session.resource('s3')
    return S3.Bucket("wellcomecollection-editorial-photography")

