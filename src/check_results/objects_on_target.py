
import botocore

BUCKETS = {
    "staging": "wellcomecollection-archivematica-staging-transfer-source",
    "production": "wellcomecollection-archivematica-transfer-source"
}


def find_objects(session, bucket,  object_keys, yield_on_found):
    for object_key in object_keys:
        full_key = f"born-digital-accessions/{object_key.strip()}.zip"
        try:
            session.client('s3').head_object(Bucket=bucket,  Key=full_key)
            if yield_on_found:
                yield full_key
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                if not yield_on_found:
                    yield full_key
            else:
                raise