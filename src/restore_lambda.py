
import os
import boto3
import json
import logging
from restore import restore_shoot_folder
from transferrer.common import get_source_bucket

logger = logging.getLogger(__name__)


def notify_shoots_restored(topic, shoot_numbers):
    for shoot in shoot_numbers:
        notify_shoot_restored(topic, shoot)


def notify_shoot_restored(topic, shoot_number):
    print(f"requesting transfer of {shoot_number} from restored queue")
    topic.publish(Message=shoot_number.strip())
    return shoot_number


def lambda_main(event, context):
    bucket = get_source_bucket(boto3.Session())
    sqs = boto3.client('sqs')
    sns = boto3.resource("sns")
    source_queue = os.getenv("SOURCE_QUEUE")

    topic = sns.Topic(arn=os.getenv("COMPLETED_TOPIC"))

    response = sqs.receive_message(
        QueueUrl=source_queue,
        # 10 is the biggest number SQS can think of.
        MaxNumberOfMessages=10
    )
    notify_shoots_restored(
        topic,
        restore_from_messages(response.get('Messages', []),  bucket, source_queue, sqs)
    )


def restore_from_messages(messages, bucket, source_queue, sqs):

    for message in messages:
        logger.info('processing message')
        try:
            shoot_number = json.loads(message['Body'])['Message']
            restore_shoot_folder(bucket, shoot_number)
            handle = message['ReceiptHandle']
            sqs.delete_message(QueueUrl=source_queue, ReceiptHandle=handle)
            yield shoot_number
        except Exception as err:
            logger.exception(err)
