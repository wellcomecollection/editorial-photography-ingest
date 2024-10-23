import boto3
import sys

BUCKETS = {
    "staging": "wellcomecollection-archivematica-staging-transfer-source",
    "production": "wellcomecollection-archivematica-transfer-source"
}


def find_objects(session, bucket,  object_keys):
    bucket = session.resource('s3').Bucket(bucket)
    for shoot_id in object_keys:
        prefix = f"born-digital-accessions/{shoot_id.strip()}"
        for obj in bucket.objects.filter(Prefix=prefix):
            if obj.key[-4:] == ".zip":
                yield obj.key


if __name__ == '__main__':
    print("\n".join(
        find_objects(boto3.Session(), BUCKETS[sys.argv[1]],  sys.stdin.readlines())
    ))
