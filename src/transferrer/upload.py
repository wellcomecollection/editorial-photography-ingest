
import logging
import os
import sys

import boto3

logger = logging.getLogger()

TARGET_BUCKET = os.getenv("TARGET_BUCKET", "wellcomecollection-archivematica-staging-transfer-source")


def upload(session, zipfile_path, target_bucket_name=TARGET_BUCKET):
    logger.info(f"uploading {zipfile_path} to {target_bucket_name}")
    get_target_bucket(session, target_bucket_name).upload_file(zipfile_path, f"born-digital-accessions/{os.path.basename(zipfile_path)}")


def get_target_bucket(session, target_bucket):
    return session.resource('s3').Bucket(target_bucket)


if __name__ == "__main__":
    upload(boto3.Session(profile_name=os.environ["AWS_TARGET_PROFILE"]), sys.argv[1])
