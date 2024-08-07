import boto3
import datetime
from elasticsearch import Elasticsearch


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
    return (f"born-digital-accessions/{hit["fields"]["bag.info.externalIdentifier"][0]}.zip" for hit in hits)


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


def get_es_client(session):
    """
    Returns an Elasticsearch client for the pipeline-storage cluster.
    """

    username = get_secret_string(
        session, secret_id="reporting/read_only/es_username"
    )
    password = get_secret_string(
        session, secret_id=f"reporting/read_only/es_password"
    )
    return Elasticsearch(f"https://d3f9c38fe7134d44b3ec7752d86b5e98.eu-west-1.aws.found.io", basic_auth=(username, password))


def get_secret_string(session, *, secret_id):
    """
    Look up the value of a SecretString in Secrets Manager.
    """
    secrets = session.client("secretsmanager")
    return secrets.get_secret_value(SecretId=secret_id)["SecretString"]


if __name__ == "__main__":
    main()
