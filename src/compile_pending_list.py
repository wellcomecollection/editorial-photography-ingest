import boto3
from elasticsearch import Elasticsearch


def get_successful_list(session, expected):
    es = get_es_client(session)
    response = es.search(
        index="storage_ingests",
        size=1000,
        query=get_query(expected),
        source=False,
        fields=["bag.info.externalIdentifier", "lastModifiedDate"]
    )
    succeeded = get_identifiers(response["hits"]["hits"])
    for shoot in expected:
        print(f'{shoot}, {shoot in succeeded}')


def get_identifiers(hits):
    return [hit["fields"]["bag.info.externalIdentifier"][0] for hit in hits]


def get_query(shoots):
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


def main():
    import sys
    get_successful_list(boto3.Session(), [f"2754_{shoot.strip()}" for shoot in sys.stdin.readlines()])


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
