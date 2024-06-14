
import logging
import os
import sys

import boto3

logger = logging.getLogger(__name__)


def get_target_bucket(session, target_bucket):
    return session.resource('s3').Bucket(target_bucket)


def upload(session, zipfile_path, target_bucket="wellcomecollection-archivematica-staging-transfer-source"):
    logger.info(f"uploading {zipfile_path} to {target_bucket}")
    get_target_bucket(session, target_bucket).upload_file(zipfile_path, f"born-digital-accessions/{os.path.basename(zipfile_path)}")


if __name__ == "__main__":
    session = boto3.Session(os.environ["AWS_TARGET_PROFILE"])
    upload(session, sys.argv[1])
