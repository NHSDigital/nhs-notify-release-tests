import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr
from helpers.logger import get_logger

logger = get_logger(__name__)

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
            return response['Items']
        except ClientError as e:
            logger.error(f"Query failed for table {table_name}: {e}")
            raise

    def put_item(self, table_name, item):
        table = self.resource.Table(table_name)
        table.put_item(Item=item)

    def get_items_by_request_id(self, table_name, request_id, nhs_number):
        table = self.resource.Table(table_name)

        items = []
        scan_kwargs = {
            "FilterExpression": (
                Attr("requestId").eq(request_id) &
                Attr("SK").begins_with("REQUEST_ITEM#") &
                Attr("nhsNumber").eq(nhs_number)
            ),
            "ProjectionExpression": "#pk",
            "ExpressionAttributeNames": {"#pk": "PK"},
        }

        while True:
            response = table.scan(**scan_kwargs)
            items.extend(response.get("Items", []))

            if "LastEvaluatedKey" not in response:
                break
            scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

        return [item["PK"] for item in items if "PK" in item]