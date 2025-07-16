import boto3
from helpers.logger import get_logger

logger = get_logger("lambda_client")

class LambdaClient:
    def __init__(self, region_name='eu-west-2'):
        self.client = boto3.client('lambda', region_name=region_name)

    def update_env_var(self, lambda_name, var_key, var_value):
        response = self.client.get_function_configuration(FunctionName=lambda_name)
        env_vars = response['Environment'].get('Variables', {})
        env_vars[var_key] = var_value

        self.client.update_function_configuration(
            FunctionName=lambda_name,
            Environment={'Variables': env_vars}
        )

        updated = self.client.get_function_configuration(FunctionName=lambda_name)
        assert updated['Environment']['Variables'][var_key] == var_value