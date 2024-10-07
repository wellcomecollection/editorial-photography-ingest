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
