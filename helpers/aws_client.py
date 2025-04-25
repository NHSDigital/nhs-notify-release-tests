import boto3
from botocore.exceptions import ClientError
from helpers.logger import get_logger

logger = get_logger("aws_client")

class AWSClient:
    def __init__(self, region_name='eu-west-2'):
        self.region_name = region_name
        self.dynamodb = boto3.client('dynamodb', region_name=region_name)
        self.s3 = boto3.client('s3', region_name=region_name)

    def get_dynamodb_table(self, table_name):
        """
        Fetches a DynamoDB table using boto3.
        """
        try:
            response = self.dynamodb.describe_table(TableName=table_name)
            logger.info(f"Fetched table info: {response['Table']['TableName']}")
            return response['Table']
        except ClientError as e:
            logger.error(f"Unable to fetch DynamoDB table {table_name}: {e}")
            raise

    def query_dynamodb(self, table_name, key_condition_expression, expression_attribute_values):
        """
        Queries a DynamoDB table with a key condition expression.
        """
        try:
            response = self.dynamodb.query(
                TableName=table_name,
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            logger.info(f"Query result: {response['Items']}")
            return response['Items']
        except ClientError as e:
            logger.error(f"Unable to query DynamoDB table {table_name}: {e}")
            raise

    def list_s3_bucket_contents(self, bucket_name, prefix=""):
        """
        Lists the contents of an S3 bucket.
        """
        try:
            response = self.s3.list_objects_v2(
                        Bucket=bucket_name,
                        Prefix=prefix
                    )
            if 'Contents' in response:
                logger.info(f"Objects in {bucket_name}: {response['Contents']}")
                return response['Contents']
            else:
                logger.info(f"No objects found in {bucket_name}")
                return []
        except ClientError as e:
            logger.error(f"Unable to list contents of S3 bucket {bucket_name}: {e}")
            raise
        
    def get_s3_object(self, bucket_name, key):
        response = self.s3.get_object(Bucket=bucket_name, Key=key)
        return response['Body'].read().decode('utf-8')