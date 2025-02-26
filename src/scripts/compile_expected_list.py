"""
Produce a list of bag.info.externalIdentifier from the list of shoots to ingests, including the "cracked" shoots, 
ie. shoots that are too big to be ingested in Archivematica and consequently split into batches
eg. shoot EP000128 resulting in bags:
EP000128_001
EP000128_002
EP000128_003

Usage - shoot_ids_list.txt being a line-separated list of shoots to ingest:

> cat shoot_ids_list.txt | python src/scripts/compile_expected_list.py

This will print out the full list of bags that we expect to be ingested into the storage-service via Archivematica
"""

import boto3
import os
from transferrer.common import get_source_bucket, shoot_number_to_folder_path
from transferrer.download import get_shoot_batches

MAX_SPACE_BYTES = os.getenv('MAX_SPACE_BYTES', 10240000000)  # maximum setting for  Lambda Ephemeral Storage

def get_expected_ingests(session: boto3.session.Session, shoot_number, max_batch_bytes):
    bucket = get_source_bucket(session)
    s3_folder = shoot_number_to_folder_path(shoot_number)
    image_batches = list(get_shoot_batches(bucket, s3_folder, max_batch_bytes))
    use_suffix = (len(image_batches) > 1)
    suffix = ""
    for ix, files in enumerate(image_batches, 1):
        if use_suffix:
            suffix = f"_{ix:03d}"
            print(f"{shoot_number}{suffix}")
        else:
            print(shoot_number)
        


def list_expected_ingests(session, shoot_number, max_batch_bytes=MAX_SPACE_BYTES/2):
    get_expected_ingests(session, shoot_number, max_batch_bytes)

if __name__ == "__main__":
    import sys
    for shoot in sys.stdin.readlines():
        list_expected_ingests(
            session=boto3.Session(profile_name="platform-developer"),
            shoot_number=shoot.strip(),
        )        
