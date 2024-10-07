import boto3
import sys

from objects_on_target import find_objects, BUCKETS

if __name__ == '__main__':
    print("\n".join(
        find_objects(boto3.Session(), BUCKETS[sys.argv[1]],  sys.stdin.readlines(), True)
    ))
