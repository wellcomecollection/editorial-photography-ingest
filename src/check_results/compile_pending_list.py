"""
Compile a list of the ingested status of the requested shoots.

Given a list of shoots that you want to have been ingested,
this will check whether they have all been successfully ingested (True)
or not (False).

A shoot may have not been ingested due to a failure, or because it
is yet to be transferred (either in progress or just not even started)

This contrasts with compile_failure_list.py, which produces a list of recent failures.

Usage:
Provide a newline separated list of shoot identifiers on STDIN,
e.g. given a file myfile.txt:
```
CP1G00D1
CP1BAAD1
CP000001
CP999999
```
where
* CP1G00D1 and CP000001 have both been ingested,
* CP1BAAD1 is somehow broken
* CP999999 is yet to be ingested

$ cat myfile.txt | python compile_pending_list.py

Output:
```
2754_CP1G00D1, True
2754_CP1BAAD1, False
2754_CP000001, True
2754_CP999999, False
```
"""

import boto3
from reporting_client import get_es_client


def get_successful_list(session, expected):
    es = get_es_client(session)
    response = es.search(
        index="storage_ingests",
        size=1000,
        query=find_shoots_query(expected),
        source=False,
        fields=["bag.info.externalIdentifier", "lastModifiedDate"]
    )
    succeeded = get_identifiers(response["hits"]["hits"])
    for shoot in expected:
        if shoot in succeeded:
            print(f'{shoot}, True')
        else:
            print(f'{shoot}, {is_cracked_shoot_successful(es, shoot)}')


def is_cracked_shoot_successful(es, shoot):
    response = es.search(
        index="storage_ingests",
        size=1000,
        query=find_subshoots_query(shoot),
        source=False,
        fields=["bag.info.externalIdentifier", "lastModifiedDate", "status.id"]
    )

    return bool(response['hits']['hits']) and all((hit['fields']['status.id'] == "succeeded" for hit in response['hits']['hits']))


def get_identifiers(hits):
    return [hit["fields"]["bag.info.externalIdentifier"][0] for hit in hits]


def find_shoots_query(shoots):
    return {
        "bool": {
          "filter": [
            {"term": {
              "status.id": "succeeded"
            }},
            {"terms": {
                  "bag.info.externalIdentifier": shoots
            }}
          ]
        }
    }


def find_subshoots_query(shoot):
    return {
        "bool": {
          "filter": [
            {"prefix": {
                  "bag.info.externalIdentifier": shoot
            }}
          ]
        }
    }


def main():
    import sys
    get_successful_list(boto3.Session(), [f"2754_{shoot.strip()}" for shoot in sys.stdin.readlines()])


if __name__ == "__main__":
    main()
