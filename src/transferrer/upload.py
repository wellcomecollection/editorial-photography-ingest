import boto3
def get_bucket():
    session = boto3.Session()
    S3 = session.resource('s3')
    return S3.Bucket("wellcomecollection-workflow-stage-upload")

