"""
Like unix touch, this updates objects in s3 without substantive change.

Call with a newline-separated list of keys, thus

echo 'born-digital-accessions/2754_CP000179.zip \n born-digital-accessions/2754_CP000181.zip' | touch.py

This is intended for use when Archivematica has ephemerally failed to accept some of the shoot zips.

A fortnightly list of failed zips is published to Slack, but you could also generate it by looking elsewhere.
"""
import sys

import boto3
import datetime

BUCKETS = {
    "staging": "wellcomecollection-archivematica-staging-transfer-source",
    "production": "wellcomecollection-archivematica-transfer-source"
}


def touch_object(session, bucket, key):
    print(f"touching: {bucket}/{key}")
    session.client('s3').copy_object(
        Bucket=bucket,
        CopySource={'Bucket': bucket,  'Key': key},
        Key=key,
        Metadata={
            'touched': datetime.datetime.now().isoformat()
        },
        MetadataDirective="REPLACE"
    )


def touch_objects(session, bucket,  object_keys):
    for object_key in object_keys:
        touch_object(session, bucket, object_key.strip())


if __name__ == '__main__':
    touch_objects(boto3.Session(), BUCKETS[sys.argv[1]],  sys.stdin.readlines())
