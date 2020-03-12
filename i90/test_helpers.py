# i90/test_helpers.py

import boto3
import pytest

from i90.config import config


class FakeFirehose:
    def __init__(self, *args, **kwargs):
        self.records = []
        return

    def put_record(self, DeliveryStreamName=None, Record=None):
        if not (DeliveryStreamName and Record):
            raise Exception()
        self.records.append(Record)


@pytest.fixture()
def redirects_table():
    client = boto3.client("dynamodb", **config.dynamo_configuration)
    db = boto3.resource("dynamodb", **config.dynamo_configuration)
    db.create_table(
        AttributeDefinitions=[{"AttributeName": "token", "AttributeType": "S"}],
        TableName=config.redirects_table,
        KeySchema=[{"AttributeName": "token", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
    )

    yield db.Table(config.redirects_table)

    client.delete_table(TableName=config.redirects_table)
