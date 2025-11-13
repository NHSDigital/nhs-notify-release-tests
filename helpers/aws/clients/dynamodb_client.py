from functools import lru_cache
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

    @lru_cache(maxsize=None)
    def _get_all_items_for_request(self, table_name, request_id):
        table = self.resource.Table(table_name)
        items = []
        scan_kwargs = {
            "FilterExpression": (
                Attr("requestId").eq(request_id) &
                Attr("SK").begins_with("REQUEST_ITEM#")
            ),
            "ProjectionExpression": "#pk, nhsNumber",
            "ExpressionAttributeNames": {"#pk": "PK"},
        }

        response = table.scan(**scan_kwargs)
        items.extend(response["Items"])

        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"], **scan_kwargs)
            items.extend(response["Items"])

        return items

    def _get_items_cached(self, table_name, request_id, nhs_number):
        all_items = self._get_all_items_for_request(table_name, request_id)
        return [item["PK"] for item in all_items if item.get("nhsNumber") == nhs_number]
