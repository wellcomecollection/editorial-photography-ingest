import os
import json
import boto3
from transferrer.transfer import transfer_shoot
import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ACCESSION_NUMBER = os.getenv("ACCESSION_NUMBER", "2754")


def lambda_handler(event, context):
    shoots = [single_handler(shoot_id) for shoot_id in get_shoot_ids(event)]
    return {
        'statusCode': 200,
        'body': shoots
    }


def single_handler(shoot_id):
    logger.info(f"transferring {shoot_id}")
    transfer_shoot(
        from_session=boto3.Session(),
        to_session=boto3.Session(),
        shoot_number=shoot_id,
        accession_number=ACCESSION_NUMBER
    )
    return shoot_id


def get_shoot_ids(event):
    for record in event['Records']:
        yield json.loads(record['body'])["Message"]