"""
Produce a list of records that have failed since a given date/time.
Usage:

> python compile_failure_list.py 2024-09-05T40:00:00

This will print out the S3 keys of all the zips that have been
transferred to Archivematica, but failed to fully process, since 1400 on the 5th of September 2024.


"""
import boto3
import datetime
from reporting_client import get_es_client


def get_failures_since(session, since_time):
    es = get_es_client(session)
    response = es.search(
        index="storage_ingests",
        size=100,
        query=get_query(since_time),
        source=False,
        fields=["bag.info.externalIdentifier", "lastModifiedDate"]
    )
    print("\n".join(get_zip_paths(response["hits"]["hits"])))


def get_zip_paths(hits):
    return (f'born-digital-accessions/{hit["fields"]["bag.info.externalIdentifier"][0]}.zip' for hit in hits)


def get_query(since_time):
    return {
        "bool": {
          "filter": [
            {"term": {
              "status.id": "failed"
            }},
            {"range": {
              "lastModifiedDate": {
                "gte": since_time
              }
            }}
          ]
        }
    }


def main():
    import sys
    get_failures_since(boto3.Session(), datetime.datetime.fromisoformat(sys.argv[1]))



if __name__ == "__main__":
    main()
