"""
Compile a list of "touchable" files, ie. that have been transferred successfully to wellcomecollection-archivematica-transfer-source
but failed to be ingested into the storage-service

Usage:
Given a list of expected_ingests generated with compile_expected_list.py

> cat expected_ingests.txt | python src/scripts/compile_touchable.py <production | staging>

"""


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


def find_objects(session, bucket, shoots_or_subshoots):
    """
    Look in a bucket to find all the zip objects corresponding to
    a list of shoots (e.g. 2754_CP000200) or subshoots (e.g. 2754_CP000300_001)
    """
    bucket = session.resource('s3').Bucket(bucket)
    for shoot_id in shoots_or_subshoots:
        object_key = f"born-digital-accessions/{shoot_id.strip()}"
        for obj in bucket.objects.filter(Prefix=object_key):
            if obj.key[-4:] == ".zip":
                yield obj.key


if __name__ == '__main__':
    objects = find_objects(boto3.Session(profile_name="digitisation-developer"), BUCKETS[sys.argv[1]], sys.stdin.readlines())
    print("\n".join(
        get_failed_subshoots(
            boto3.Session(profile_name="platform-developer"), objects)
    ))
