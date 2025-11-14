import json
import tempfile
import uuid
from helpers.aws.clients.dynamodb_client import DynamoDBClient
from helpers.aws.clients.s3_client import S3Client
from helpers.aws.clients.lambda_client import LambdaClient
from helpers.aws.clients.ssm_client import SSMClient
from helpers.constants import get_env, get_client
from helpers.logger import get_logger
from helpers.evidence import save_evidence
from helpers.test_data.quota_data import QuotaData
from helpers.generators import Generators
from datetime import datetime
from pathlib import Path

logger = get_logger(__name__)

class AWSClient:
    def __init__(self, region_name='eu-west-2'):
        self.dynamo = DynamoDBClient(region_name)
        self.lambda_ = LambdaClient(region_name)
        self.s3 = S3Client(region_name)
        self.ssm = SSMClient(region_name='eu-west-2')

    def list_s3_bucket_contents(self, bucket_name, prefix=""):
        response = self.s3.list_objects(bucket_name, prefix)
        if 'Contents' in response:
            return response['Contents']
        else:
            return []

    def get_s3_object(self, bucket_name, key):
        response = self.s3.get_object(bucket_name, key)
        return response
    
    def upload_file_to_s3(self, bucket_name, destination, local_file):
        self.s3.upload_file(bucket_name, destination, location=local_file)

    def trigger_lambda(self, lambda_name):
        test_event = {
            "key1": "value1",
            "key2": "value2"
        }
        response = self.lambda_.invoke_lambda(lambda_name, test_event)
        return response

    def create_quotas(self):
        environment = get_env()
        client = get_client()
        table_name = f"comms-{environment}-api-stg-quota"
        quotas = [
            QuotaData(supplier="NHSAPP", communication_type="NHSAPP", client_id=client),
            QuotaData(supplier="GOVUK_NOTIFY", communication_type="EMAIL", client_id=client),
            QuotaData(supplier="GOVUK_NOTIFY", communication_type="SMS", client_id=client),
            QuotaData(supplier="GOVUK_NOTIFY", communication_type="LETTER", client_id=client),
            QuotaData(supplier="MBA", communication_type="LETTER", client_id=client),
            QuotaData(supplier="SYNERTEC", communication_type="LETTER", client_id=client),
            QuotaData(supplier="PRECISIONPROCO", communication_type="LETTER", client_id=client),
            QuotaData(supplier="PRERENDERMOCK", communication_type="LETTER", client_id=client),
        ]
        for quota in quotas:
            quota_body = Generators.generate_quota(quota, environment)
            self.dynamo.put_item(table_name, quota_body)

    def update_client_config(self):
        environment = get_env()
        client = get_client()
        client_config_path = f"/comms/{environment}/clients/{client}"
        if environment == "int":
            client_config_value = {
                "clientId":"apim_integration_test",
                "name":"APIM Integration Test",
                "allowAlternativeContactDetails": True,
                "allowAnonymousPatient": True,
                "allowOdsOverride": True,
                "meshMailboxId": "X26OT282",
                "meshWorkflowIdSuffix": "TEST",
                "senderOdsCode":"T9A9F",
                "allowRfrOverride": False,
                "ignoreSecurityFlag": False
            }
        else:
            client_config_value = {
                "clientId": client,
                "name": "APIM Integration Test",
                "allowAlternativeContactDetails": True,
                "allowAnonymousPatient": True,
                "allowOdsOverride": True,
                "meshMailboxId": "X26OT234",
                "meshWorkflowIdSuffix": "TEST",
                "senderOdsCode":"X26",
                "allowRfrOverride": False,
                "ignoreSecurityFlag": False
            }
        
        ssm_value = json.dumps(client_config_value)
        self.ssm.put_parameter(client_config_path, ssm_value)
        logger.info(f"Updated SSM parameter at {client_config_path} with value {ssm_value}")

        self.lambda_.update_env_var(f'comms-{environment}-api-oa3-commsapi-apim-create-message', 'TEST_VALUE', str(uuid.uuid1()))
        self.lambda_.update_env_var(f'comms-{environment}-api-oa3-commsapi-apim-create-request', 'TEST_VALUE', str(uuid.uuid1()))
        self.lambda_.update_env_var(f'comms-{environment}-api-ecl-enrich', 'TEST_VALUE', str(uuid.uuid1()))
        logger.info("Reset client config cache in message send lambdas")

    def upload_templates(self):
        environment = get_env()
        template_directory = Path("resources/templates")
        file_names = [f.name for f in template_directory.iterdir() if f.is_file()]

        for file_name in file_names:
            if file_name.endswith(".json"):
                bucket_name = f"comms-736102632839-eu-west-2-{environment}-api-stg-comms-mgr"
                images = f"{template_directory}/images/qr_code.svg"
                s3_directory = f"templates/{file_name.replace("_template.json", "")}/"
                destination = f"{s3_directory}{file_name}"
                self.s3.upload_file(bucket_name, local_file=images , s3_file=f"{s3_directory}images/qr_code.svg")
            elif file_name.endswith("csv"):
                bucket_name = f"comms-736102632839-eu-west-2-{environment}-api-lspl-letter-csv"
                if file_name.startswith("mba"):
                    s3_directory = "MBA/fields/"
                elif file_name.startswith("synertec"):
                    s3_directory = "SYNERTEC/fields/"
                elif file_name.startswith("precisionproco"):
                    s3_directory = "PRECISIONPROCO/fields/"

                destination = f"{s3_directory}{file_name}"
            
            self.s3.upload_file(bucket_name, local_file=template_directory / file_name, s3_file=destination)
            logger.info(f"Uploaded template {file_name} to S3 bucket {bucket_name} at {destination}")

    def update_routing_configs(self, template_directory, file_name):
        client = get_client()
        with open(template_directory / file_name) as f:
            config = json.load(f)
        config["clientId"] = client
        assert config["clientId"] == client
        logger.info(f"Updated routing config {file_name} with clientId {client}")

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmp_file:
            json.dump(config, tmp_file, indent=2)
            tmp_file.flush()
            tmp_path = Path(tmp_file.name)
        return tmp_path

    def upload_routing_configs(self):
        environment = get_env()
        template_directory = Path("resources/routing_configs")
        file_names = [f.name for f in template_directory.iterdir() if f.is_file()]

        for file_name in file_names:
            bucket_name = f"comms-736102632839-eu-west-2-{environment}-api-stg-comms-mgr"
            s3_directory = f"sending-groups/{file_name.replace('_routing-config.json','')}"
            destination = f"{s3_directory}/{file_name}"
            routing_config = self.update_routing_configs(template_directory, file_name)
            self.s3.upload_file(bucket_name, local_file=routing_config, s3_file=destination)
            logger.info(f"Uploaded routing config {file_name} to S3 bucket {bucket_name} at {destination}")

    def filter_rules(self, enabled):
        environment = get_env()
        client = get_client()
        table_name = f"comms-{environment}-api-stg-comms-filter-rules"
        item = {
            "PK": "LETTER",
            "SK": "NHS_NOTIFY_RELEASE_TESTING#AUTOMATION_FILTER_RULE",
            "active": enabled,
            "clientId": client,
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
        self.lambda_.update_env_var(f'comms-{environment}-api-ecl-enrich', 'LOG_LEVEL', var_value)

    def query_dynamodb_by_request_item(self, request_item):
        environment = get_env()
        if "REQUEST_ITEM#" in request_item:
            request_item = request_item.split("#")[1]
        table_name = f"comms-{environment}-api-stg-comms-mgr"
        key_condition = "PK = :PK"
        expression_values = {":PK": {"S": f"REQUEST_ITEM#{request_item}"}}
        response = self.dynamo.query(table_name, key_condition, expression_values)
        return response

    def get_items_by_request_id(self, request_id, nhs_number):
        environment = get_env()
        table_name = f"comms-{environment}-api-stg-comms-mgr"
        return self.dynamo._get_items_cached(table_name, request_id, nhs_number)

    def verify_precision_proco_letter(self, user):
        environment = get_env()
        bucket_name = f"comms-736102632839-eu-west-2-{environment}-api-lspl-letter-csv"
        file = f"PRECISIONPROCO/uploaded/precisionproco-release-testing/{user.batch_id}.csv" 
        content = self.get_s3_object(bucket_name, file).decode('utf-8')
        assert user.personalisation in content
        save_evidence(content, f"{user.personalisation}/precision_proco_letter.csv")
        logger.info(f"Verified Precision Proco letter for user {user.nhs_number}")
        
    def verify_mba_letter(self, user):
        environment = get_env()
        bucket_name = f"comms-736102632839-eu-west-2-{environment}-api-lspl-letter-csv"       
        file = f"MBA/uploaded/mba-release-testing/{user.batch_id}.csv"
        content = self.get_s3_object(bucket_name, file).decode('utf-8')
        assert user.personalisation in content
        save_evidence(content, f"{user.personalisation}/mba.csv")
        logger.info(f"Verified MBA letter for user {user.nhs_number}")

    def verify_synertec_letter(self, user):
        environment = get_env()
        bucket_name = f"comms-736102632839-eu-west-2-{environment}-api-lspl-letter-csv"
        file = f"SYNERTEC/uploaded/synertec-release-testing/{user.batch_id}.csv"
        content = self.get_s3_object(bucket_name, file).decode('utf-8')
        assert user.personalisation in content
        save_evidence(content, f"{user.personalisation}/synertec.csv")
        logger.info(f"Verified Synertec letter for user {user.nhs_number}")

    def verify_pdf_rendering_letter_test_account(self, user):
        environment = get_env()
        bucket_name = f"comms-736102632839-eu-west-2-{environment}-api-stg-pdf-pipeline"
        prefix = "PRERENDERMOCK/batches/"
        response = self.list_s3_bucket_contents(bucket_name=bucket_name, prefix=prefix)
        #Get the most recent file
        latest = max(response, key=lambda x: x["LastModified"])
        content = self.get_s3_object(bucket_name, latest["Key"])
        save_evidence(content, f"{user.personalisation}/test_pdf_rendering_letter.tgz")

    def verify_pdf_rendering_letter_mgmt_account(self, user):
        environment = get_env()
        date = datetime.now().strftime("%Y-%m-%d")
        bucket_name = "comms-pl-886194799418-eu-west-2-pl-mgmt-acct-sftpdev-sftpdev"
        prefix = f"PRERENDERMOCK/Incoming/{environment}/apim_integration_test_client_id_ReleaseTesting/BSL/{date}/"
        response = self.list_s3_bucket_contents(bucket_name=bucket_name, prefix=prefix)
        #Get the most recent file
        latest = max(response, key=lambda x: x["LastModified"])
        content = self.get_s3_object(bucket_name, latest["Key"])
        save_evidence(content, f"{user.personalisation}/mgmt_pdf_rendering_letter.tgz")
