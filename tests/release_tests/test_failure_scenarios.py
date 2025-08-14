import time
import uuid
from helpers.test_data.user_data import UserData
from helpers.aws.aws_client import AWSClient
from helpers.api.apim_request import APIHelper
from helpers.constants import (
    NHS_NUMBER_INFORMALLY_DEAD,
    NHS_NUMBER_FORMALLY_DEAD,
    NHS_NUMBER_SFLAG,
    NHS_NUMBER_NOT_IN_PDS,
    NHS_NUMBER_INVALIDATED,
    NHS_NUMBER_NO_VALID_PLANS,
    NHS_NUMBER_EXIT_CODE
)
from helpers.logger import get_logger

logger = get_logger(__name__)

def test_failure_scenarios(api_client):
    api_helper = APIHelper(api_client)
    aws_client = AWSClient()

    # Set up test data
    test_users = [
        UserData(NHS_NUMBER_INFORMALLY_DEAD, str(uuid.uuid1()), failed_reason="Patient is informally dead", personalisation="Failure scenarios"),
        UserData(NHS_NUMBER_FORMALLY_DEAD, str(uuid.uuid1()), failed_reason="Patient is formally dead", personalisation="Failure scenarios"),
        UserData(NHS_NUMBER_SFLAG, str(uuid.uuid1()), failed_reason="flagged", personalisation="Failure scenarios"),
        UserData(NHS_NUMBER_NOT_IN_PDS, str(uuid.uuid1()), failed_reason="Patient does not exist in PDS", personalisation="Failure scenarios"),
        UserData(NHS_NUMBER_INVALIDATED, str(uuid.uuid1()), failed_reason="Patient record invalidated", personalisation="Failure scenarios"),
        UserData(NHS_NUMBER_NO_VALID_PLANS, str(uuid.uuid1()), failed_reason="No valid request item plans were generated", personalisation="Failure scenarios"),
        UserData(NHS_NUMBER_EXIT_CODE, str(uuid.uuid1()), failed_reason="Patient has exit code", personalisation="Failure scenarios"),
    ]

    body = api_helper.construct_batch_message_body(test_users)
    api_helper.send_and_verify_message_batch_request(body, test_users, NHS_NUMBER_NO_VALID_PLANS, status='failed')

    for user in test_users:
        ddb_records = aws_client.query_dynamodb_by_request_item(user.request_item)
        for record in ddb_records:
            if user.failed_reason != record.get('failedReason', {}).get('S'):
                continue
            else:
                assert user.failed_reason == record.get('failedReason', {}).get('S')
                logger.info(f"Verified failure reason for {user.nhs_number}: {user.failed_reason}")
                break
