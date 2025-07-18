import json
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

    def invoke_lambda(self, lambda_name, payload, invocation_type='RequestResponse'):
        """
        Invokes a Lambda function with the given payload.

        :param lambda_name: The name or ARN of the Lambda function.
        :param payload: A dict representing the event to send to the Lambda.
        :param invocation_type: Invocation type - 'RequestResponse' (default), 'Event', or 'DryRun'.
        :return: The response payload as a dict if available.
        """
        logger.info(f"Invoking Lambda: {lambda_name} with payload: {payload}")
        response = self.client.invoke(
            FunctionName=lambda_name,
            InvocationType=invocation_type,
            Payload=json.dumps(payload).encode('utf-8')
        )

        if 'Payload' in response:
            response_payload = response['Payload'].read().decode('utf-8')
            logger.info(f"Lambda response: {response_payload}")
            try:
                return json.loads(response_payload)
            except json.JSONDecodeError:
                return response_payload
        return response