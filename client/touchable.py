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
    """
    Given a list of shoots/subshoots, (s3 keys),
    return any that have not successfully been ingested.
    """
    es = get_es_client(session)
    # make it a list, in case it's a generator.  We need to go over it more than once.
    subshoots = list(subshoots)
    # subshoots is a list of S3 Keys - e.g. born-digital-accessions/2754_CP000200.zip
    # In order to query the storage_ingests database, we need the base name of the
    # file - e.g. 2754_CP000200.
    # so knock off the leading/path/ and the .suffix
    ids = [s[:-4].rpartition('/')[2] for s in  subshoots]

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
    """
    Look in a bucket to find all the zip objects corresponding to
    a list of shoot numbers (e.g. 2754_CP000200).

    These objects may be named with the shoot number alone, e.g. 2754_CP000200.zip
    or may be part of a broken-up shoot with a suffix, e.g. 2754_CP000200_001.zip
    """
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
