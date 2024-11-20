import boto3
import sys
import os
from compile_pending_list import find_shoots_query, get_identifiers

from reporting_client import get_es_client

BUCKETS = {
    "staging": "wellcomecollection-archivematica-staging-transfer-source",
    "production": "wellcomecollection-archivematica-transfer-source"
}

def get_failed_subshoots(session, subshoots):
    es = get_es_client(session)
    subshoots = list(subshoots)
    ids = [s[:-4].partition('/')[2] for s in  subshoots]

    response = es.search(
        index="storage_ingests",
        size=1000,
        query=find_shoots_query(ids),
        source=False,
        fields=["bag.info.externalIdentifier", "lastModifiedDate"]
    )
    succeeded = get_identifiers(response["hits"]["hits"])
    for pair in zip(subshoots, ids):
        if pair[1] not in succeeded:
            yield pair[0]

def find_objects(session, bucket,  object_keys):
    bucket = session.resource('s3').Bucket(bucket)
    for shoot_id in object_keys:
        prefix = f"born-digital-accessions/{shoot_id.strip()}"
        for obj in bucket.objects.filter(Prefix=prefix):
            if obj.key[-4:] == ".zip":
                yield obj.key


if __name__ == '__main__':
    objects = find_objects(boto3.Session(profile_name="digitisation-developer"), BUCKETS[sys.argv[1]],  sys.stdin.readlines())
    print("\n".join(
        get_failed_subshoots(
            boto3.Session(profile_name="platform-developer"), objects)
    ))
