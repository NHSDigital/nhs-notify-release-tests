from helpers.aws.clients.dynamodb_client import DynamoDBClient
from helpers.aws.clients.s3_client import S3Client
from helpers.aws.clients.lambda_client import LambdaClient
from helpers.logger import get_logger

logger = get_logger(__name__)

class AWSClient:
    def __init__(self, region_name='eu-west-2'):
        self.dynamo = DynamoDBClient(region_name)
        self.lambda_ = LambdaClient(region_name)
        self.s3 = S3Client(region_name)

    def filter_rules(self, enabled):
        table_name = 'comms-uat-api-stg-comms-filter-rules'
        item = {
            "PK": "LETTER",
            "SK": "NHS_NOTIFY_RELEASE_TESTING#AUTOMATION_FILTER_RULE",
            "active": enabled,
            "clientId": "apim_integration_test_client_id",
            "description": "Filter rule to stop processing letter requests if enabled",
            "detailType": "LETTER",
            "fields": {
                "addressLine1": {
                "pattern": "^.*$"
                },
                "postcode": {
                    "pattern": "^.*$"
                }
            },
            "ruleId": "NHS Notify Automated Release Regression",
            "ticketReference": "NHS Notify Release Regression"
    }

        self.dynamo.put_item(table_name, item)

        key_condition = "PK = :PK"
        expression_values = {
            ":PK": {"S": "LETTER"}
        }

        result = self.dynamo.query(table_name, key_condition, expression_values)

        for i in result:
            if i['SK']['S'] == 'NHS_NOTIFY_RELEASE_TESTING#AUTOMATION_FILTER_RULE':
                assert i['active']['BOOL'] is enabled

        var_value = 'debug' if enabled else 'info'
        self.lambda_.update_env_var('comms-uat-api-ecl-enrich', 'LOG_LEVEL', var_value)

    def trigger_letters_polling_lambdas(self):
        self.trigger_lambda('comms-uat-api-nsp-letters-notify-polling')
        self.trigger_lambda('comms-uat-api-lspl-sftppoll')
        self.trigger_lambda('comms-uat-api-lss-sftppollsynertec')
        self.trigger_lambda('comms-uat-api-lspp-sftppollprecisionproco')
        logger.info("Triggered all letter polling lambdas")

    def query_dynamodb_by_request_item(self, request_item):
        table_name = "comms-uat-api-stg-comms-mgr"
        key_condition = "PK = :PK"
        expression_values = {":PK": {"S": f"REQUEST_ITEM#{request_item}"}}
        response = self.dynamo.query(table_name, key_condition, expression_values)
        return response

    def list_s3_bucket_contents(self, bucket_name, prefix=""):
        response = self.s3.list_objects(bucket_name, prefix)
        if 'Contents' in response:
            return response['Contents']
        else:
            return []

    def get_s3_object(self, bucket_name, key):
        response = self.s3.get_object(bucket_name, key)
        return response
    
    def trigger_lambda(self, lambda_name):
        test_event = {
            "key1": "value1",
            "key2": "value2"
        }
        response = self.lambda_.invoke_lambda(lambda_name, test_event)
        return response

    def verify_precision_proco_letter(self, user):
        bucket_name = "comms-736102632839-eu-west-2-uat-api-lspl-letter-csv"
        file = f"PRECISIONPROCO/uploaded/pp-release-testing/{user.batch_id}.csv" 
        content = self.get_s3_object(bucket_name, file)
        assert user.personalisation in content
        logger.info(f"Verified Precision Proco letter for user {user.nhs_number}")
        
    def verify_mba_letter(self, user):
        bucket_name = "comms-736102632839-eu-west-2-uat-api-lspl-letter-csv"       
        file = f"MBA/uploaded/hh-release-testing/{user.batch_id}.csv"
        content = self.get_s3_object(bucket_name, file)
        assert user.personalisation in content
        logger.info(f"Verified MBA letter for user {user.nhs_number}")

    def verify_synertec_letter(self, user):
        bucket_name = "comms-736102632839-eu-west-2-uat-api-lspl-letter-csv"
        file = f"SYNERTEC/uploaded/synertec-release-testing/{user.batch_id}.csv"
        content = self.get_s3_object(bucket_name, file)
        assert user.personalisation in content
        logger.info(f"Verified Synertec letter for user {user.nhs_number}")