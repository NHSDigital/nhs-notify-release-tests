import boto3
from helpers.logger import get_logger

logger = get_logger(__name__)

class S3Client:
    def __init__(self, region_name='eu-west-2'):
        self.client = boto3.client('s3', region_name=region_name)

    def list_objects(self, bucket_name, prefix=""):
        return self.client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    def get_object(self, bucket_name, key):
        response = self.client.get_object(Bucket=bucket_name, Key=key)
        return response['Body'].read()