import boto3


def create_users_table():
    """Create a Users table in DynamoDB.
    Before running this function, make sure you have the aws credentials set up in your machine.
    """
    dynamodb = boto3.resource("dynamodb")

    table = dynamodb.create_table(
        TableName="users",
        KeySchema=[
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "first_name", "KeyType": "RANGE"},
            {"AttributeName": "last_name", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "first_name", "AttributeType": "S"},
            {"AttributeName": "last_name", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    table.wait_until_exists()
