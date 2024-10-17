from elasticsearch import Elasticsearch

def get_es_client(session):
    """
    Returns an Elasticsearch client for the reporting cluster.
    """
    username = get_secret_string(
        session, secret_id="reporting/read_only/es_username"
    )
    password = get_secret_string(
        session, secret_id=f"reporting/read_only/es_password"
    )
    host = get_secret_string(
        session, secret_id=f"reporting/es_host"
    )
    return Elasticsearch(f"https://{host}", basic_auth=(username, password))


def get_secret_string(session, *, secret_id):
    return session.client("secretsmanager").get_secret_value(SecretId=secret_id)["SecretString"]
