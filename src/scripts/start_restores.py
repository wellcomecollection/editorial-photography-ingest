"""
First step in ingesting corporate/editorial photography from wellcomecollection-editorial-photography S3 bucket 
into the storage-service via Archivematica. 

Usage:

Provide a newline separated list of shoots to ingest on STDIN,
e.g. given a file shoot_ids_list.txt:
```
CP003481
CP003484
CP003488
CP003490
CP003500 
```
> cat shoot_ids_list.txt | src/scripts/start_restores.py
"""

import sys
import boto3


def post_messages(session, shoot_numbers):
    sns = session.resource("sns")
    topic = sns.Topic(f"arn:aws:sns:eu-west-1:760097843905:restore_shoots-production")
    for shoot_number in shoot_numbers:
        print(f"requesting restore of {shoot_number}")
        topic.publish(Message=shoot_number.strip())


if __name__ == "__main__":
    post_messages(boto3.Session(), sys.stdin.readlines())
