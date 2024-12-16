"""
Given a list of shoot numbers, return any of them that have not been transferred

This script assumes that the presence of any part of the shoot on the target system
implies that it has been transferred. i.e. that if a shoot is a large one that needs to be
broken apart, then it does not check whether all parts have been successfully transferred.
"""

import boto3
import sys

BUCKETS = {
    "staging": "wellcomecollection-archivematica-staging-transfer-source",
    "production": "wellcomecollection-archivematica-transfer-source"
}

def find_missing_objects(session, bucket,  object_keys):
    bucket = session.resource('s3').Bucket(bucket)
    for shoot_id in object_keys:
        prefix = f"born-digital-accessions/{shoot_id.strip()}"
        try:
            next(iter(bucket.objects.filter(Prefix=prefix)))
        except StopIteration:
            yield shoot_id.strip()


if __name__ == '__main__':
    print("\n".join(
        find_missing_objects(boto3.Session(), BUCKETS[sys.argv[1]],  sys.stdin.readlines())
    ))
