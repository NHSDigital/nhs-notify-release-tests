import boto3
from botocore.exceptions import ClientError
from helpers.logger import get_logger

logger = get_logger("dynamodb_client")

class DynamoDBClient:
    def __init__(self, region_name='eu-west-2'):
        self.client = boto3.client('dynamodb', region_name=region_name)
        self.resource = boto3.resource('dynamodb', region_name=region_name)

    def query(self, table_name, key_condition_expression, expression_attribute_values):
        try:
            response = self.client.query(
                TableName=table_name,
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            logger.info(f"Query result: {response['Items']}")
            return response['Items']
        except ClientError as e:
            logger.error(f"Query failed for table {table_name}: {e}")
            raise

    def put_item(self, table_name, item):
        table = self.resource.Table(table_name)
        table.put_item(Item=item)
