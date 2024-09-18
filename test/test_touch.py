import datetime

import pytest
import boto3
import pyfakefs
import touch
from moto import mock_aws
from freezegun import freeze_time

@mock_aws
def test_raises_on_unknown_object(moto_session, target_bucket):
    with pytest.raises(Exception):
        touch.touch_object(moto_session, target_bucket.name, "baadf00d.zip")


def yesterday():
    return datetime.datetime.now() - datetime.timedelta(days = 1)

@mock_aws
def test_updates_existing_object(moto_session, target_bucket, fs):
    fs.create_file("g00dcafe.zip")
    with freeze_time(yesterday()):
        target_bucket.upload_file("g00dcafe.zip", "g00dcafe.zip")
    before = list(target_bucket.objects.all())[0]
    touch.touch_object(moto_session, target_bucket.name, "g00dcafe.zip")
    after = list(target_bucket.objects.all())[0]
    assert after.last_modified > before.last_modified



