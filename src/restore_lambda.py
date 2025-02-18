
import os
import boto3
import json
import logging
from restore import restore_shoot_folder
from transferrer.common import get_source_bucket

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
SHOOTS_PER_DAY = 60


def notify_shoots_restored(topic, shoot_numbers):
    for shoot in shoot_numbers:
        notify_shoot_restored(topic, shoot)


def notify_shoot_restored(topic, shoot_number):
    logger.info(f"requesting transfer of {shoot_number} from restored queue")
    topic.publish(Message=shoot_number.strip())
    return shoot_number


def lambda_main(event, context):
    bucket = get_source_bucket(boto3.Session())
    sqs = boto3.client('sqs')
    sns = boto3.resource("sns")
    source_queue = os.getenv("SOURCE_QUEUE")

    topic = sns.Topic(arn=os.getenv("COMPLETED_TOPIC"))

    notify_shoots_restored(
        topic,
        restore_from_messages(get_messages(sqs, source_queue, SHOOTS_PER_DAY),  bucket, source_queue, sqs)
    )


def get_messages(sqs, source_queue,  count):
    logger.info(f"pulling messages from {source_queue}")
    received = 0
    while received < count:
        response = sqs.receive_message(
            QueueUrl=source_queue,
            # 10 is the biggest number SQS can think of.
            # but it is not guaranteed that this call will actually pull 10,
            # so we keep going until we've either managed to pull _count_ messages
            # or we don't get any messages, implying that the queue is now empty.
            MaxNumberOfMessages=min(10, count - received),
            WaitTimeSeconds=20
        )
        messages = response.get('Messages', [])
        message_count = len(messages)
        if message_count == 0:
            logger.info(f"pulled zero messages, quitting")
            break
        received += message_count
        logger.info(f"pulled {message_count}, total {received}")
        for message in messages:
            yield message


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
