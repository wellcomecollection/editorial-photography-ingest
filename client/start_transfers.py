import sys
import boto3


def post_messages(session, environment, shoot_numbers):
    sns = session.resource("sns")
    topic = sns.Topic(f"arn:aws:sns:eu-west-1:404315009621:transfer-shoots-{environment}")
    for shoot_number in shoot_numbers:
        print(f"requesting transfer of {shoot_number}")
        topic.publish(Message=shoot_number.strip())


if __name__ == "__main__":
    post_messages(boto3.Session(), sys.argv[1], sys.stdin.readlines())
