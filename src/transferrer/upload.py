
import logging
import os
import sys

import boto3

logger = logging.getLogger(__name__)


def get_target_bucket(target_bucket):
    session = boto3.Session()
    S3 = session.resource('s3', config=)
    return S3.Bucket(target_bucket)


def upload(zipfile_path, target_bucket="wellcomecollection-workflow-stage-upload"):
    logger.info(f"uploading {zipfile_path} to {target_bucket}")
    get_target_bucket(target_bucket).upload_file(zipfile_path, f"ep_transfer/{os.path.basename(zipfile_path)}")


if __name__ == "__main__":
    upload(sys.argv[1])
