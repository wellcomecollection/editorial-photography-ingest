"""
Like unix touch, this updates objects in s3 without substantive change.

This is intended for use when Archivematica has ephemerally failed to accept some of the shoot zips.

A fortnightly list of failed zips is published to Slack (TBC) but you could also generate it by looking elsewhere, 
eg. the storage-service's ingests dashboard in the reporting cluster

"""

import sys
import os
import datetime
import json
import logging
import boto3


logger = logging.getLogger(__name__)


BUCKETS = {
    "staging": "wellcomecollection-archivematica-staging-transfer-source",
    "production": "wellcomecollection-archivematica-transfer-source"
}


def touch_object(session, bucket, key):
    print(f"touching: {bucket}/{key}")
    obj = session.resource('s3').Bucket(bucket).Object(key)
    obj.copy(
        CopySource={'Bucket': bucket,  'Key': key},
        ExtraArgs={
            'Metadata': {
                'touched': datetime.datetime.now().isoformat()
            },
            "MetadataDirective": "REPLACE"
        }
    )


def touch_objects(session, bucket,  object_keys):
    for object_key in object_keys:
        touch_object(session, bucket, object_key.strip())


def lambda_main(event, context):
    target_bucket = os.getenv("TARGET_BUCKET")
    # 10 is the biggest number SQS can think of.
    message_count = int(os.getenv("MESSAGES_PER_BATCH", 10))
    source_queue = os.getenv("SOURCE_QUEUE")
    sqs = boto3.client('sqs')
    response = sqs.receive_message(
        QueueUrl=source_queue,
        MaxNumberOfMessages=message_count
    )
    messages = response.get('Messages', [])
    session = boto3.Session()
    for message in messages:
        try:
            key = json.loads(message['Body'])['Message']
            handle = message['ReceiptHandle']
            touch_object(session, target_bucket, key)
            sqs.delete_message(QueueUrl=source_queue, ReceiptHandle=handle)
        except Exception as err:
            logger.exception(err)


if __name__ == '__main__':
    touch_objects(boto3.Session(), BUCKETS[sys.argv[1]],  sys.stdin.readlines())
