"""
Pulls messages from the restored queue and notifies the transfer queue.

Archivematica can only handle about 20 transfers at a time, and about 60 in a day.
This Lambda is the throttle between the restorer restoring a whole day of material
and the transferrer which will try to transfer records as fast as the queue provides them.

This also allows the restoration to complete before attempting a transfer.

The restorer lambda pulls a full day's batch of transfers from the restore queue in the evening
and populates the queue_shoot_transfers with them.

The following day, this throttle pulls those requested transfers off the queue at a manageable rate,
and puts them on the "transfer-shoots" queue, which triggers the actual transfer.

"""
import os
import boto3
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_main(event, context):
    source_queue = os.getenv("SOURCE_QUEUE")
    target_topic = os.getenv("TARGET_TOPIC")
    sns = boto3.resource("sns")
    topic = sns.Topic(target_topic)
    sqs = boto3.client('sqs')

    for message in push_messages(topic, get_messages(sqs, source_queue, 10)):
        sqs.delete_message(QueueUrl=source_queue, ReceiptHandle=message['ReceiptHandle'])


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


def push_messages(topic, messages):
    for message in messages:
        yield push_message(topic, message)


def push_message(topic, message):
    shoot_number = json.loads(message['Body'])['Message']
    logger.info(f"requesting transfer of {shoot_number} from restored queue")
    topic.publish(Message=shoot_number.strip())
    return message

