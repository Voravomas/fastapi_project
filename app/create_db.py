import boto3
from keys import ACCESS_ID, ACCESS_KEY


def create_movie_table(dynamodb):
    table = dynamodb.create_table(
        TableName='Employee',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'N'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table


if __name__ == "__main__":
    dynamo_db = boto3.resource('dynamodb', endpoint_url="http://dynamodb.eu-central-1.amazonaws.com/",
                               region_name='eu-central-1',
                               aws_access_key_id=ACCESS_ID,
                               aws_secret_access_key=ACCESS_KEY)
    print(create_movie_table(dynamodb=dynamo_db))
