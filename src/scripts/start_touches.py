"""
Given a list of "touchable" files generated with compile_touchable.py, this queues them to be touched in batches of 10 on a schedule

Usage :

> cat touchables.txt | src/scripts/start_touches.py

"""

import sys
import boto3


def post_messages(session, environment, shoot_numbers):
    sns = session.resource("sns")
    topic = sns.Topic(f"arn:aws:sns:eu-west-1:404315009621:touch_shoots-{environment}")
    for shoot_number in shoot_numbers:
        print(f"requesting touch of {shoot_number}")
        topic.publish(Message=shoot_number.strip())


if __name__ == "__main__":
    post_messages(boto3.Session(), sys.argv[1], sys.stdin.readlines())
