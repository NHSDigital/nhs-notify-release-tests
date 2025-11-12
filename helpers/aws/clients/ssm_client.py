import boto3
from helpers.logger import get_logger

logger = get_logger(__name__)

class SSMClient:
    def __init__(self, region_name='eu-west-2'):
        self.client = boto3.client('ssm', region_name=region_name)

    def put_parameter(self, name, value, type='SecureString', overwrite=True):
        return self.client.put_parameter(
                Name=name,
                Value=value,
                Type=type,
                Overwrite=overwrite
        )
