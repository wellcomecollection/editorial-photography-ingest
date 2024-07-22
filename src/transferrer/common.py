import os
import boto3
import botocore

SOURCE_BUCKET = "wellcomecollection-editorial-photography"


def get_source_bucket(session: boto3.session.Session, max_connections=10):
    return get_source_client(session, max_connections).Bucket(SOURCE_BUCKET)


def get_source_client(session: boto3.session.Session, max_connections):
    return session.resource('s3', config=botocore.config.Config(
        max_pool_connections=max_connections
    ))


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


def discard_file(file):
    """
    The metadata files from the original upload are not wanted, and should be discarded
    shoot.csv is one such file...

    >>> discard_file("/path/to/shoot.csv")
    True

    ...as is an XML file that is eponymous with the shoot number.

    >>> discard_file("/path/to/CP_000159.xml")
    True

    For ease of writing, all XML files are discarded.

    >>> discard_file("/path/to/HelloWorld.xml")
    True

    Similarly, although in real data, the CSV file is always "shoot.csv", there are some test shoots
    with a different name for this file, so all CSVs are discarded
    >>> discard_file("/path/to/shoot - 1381-06-13 wat.csv")
    True

    The intent is to retain *.tif files...

    >>> discard_file("/path/to/C0007851.tif")
    False

    ...but this function focuses on discarding the files we know we don't want
    rather than retaining certain files, in case a future ingest needs to
    import other formats, such as video.

    >>> discard_file("/path/to/C0007851.mpg")
    False

    """
    return file[-4:] in (".csv", ".xml")
