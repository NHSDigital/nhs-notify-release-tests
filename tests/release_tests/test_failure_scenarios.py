import time
import uuid
from helpers.test_data.user_data import UserData
from helpers.aws.aws_client import AWSClient
from helpers.api.apim_request import APIHelper
from helpers.evidence import save_evidence
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
        UserData(NHS_NUMBER_INFORMALLY_DEAD, str(uuid.uuid1()), failed_reason="Patient is informally dead", personalisation="Failure Scenarios"),
        UserData(NHS_NUMBER_FORMALLY_DEAD, str(uuid.uuid1()), failed_reason="Patient is formally dead", personalisation="Failure Scenarios"),
        UserData(NHS_NUMBER_SFLAG, str(uuid.uuid1()), failed_reason="flagged", personalisation="Failure Scenarios"),
        UserData(NHS_NUMBER_NOT_IN_PDS, str(uuid.uuid1()), failed_reason="Patient does not exist in PDS", personalisation="Failure Scenarios"),
        UserData(NHS_NUMBER_INVALIDATED, str(uuid.uuid1()), failed_reason="Patient record invalidated", personalisation="Failure Scenarios"),
        UserData(NHS_NUMBER_NO_VALID_PLANS, str(uuid.uuid1()), failed_reason="No valid request item plans were generated", personalisation="Failure Scenarios"),
        UserData(NHS_NUMBER_EXIT_CODE, str(uuid.uuid1()), failed_reason="Patient has exit code", personalisation="Failure Scenarios"),
    ]

    body = api_helper.construct_batch_message_body(test_users)
    api_helper.send_and_verify_message_batch_request(body, test_users, status='failed')

    for user in test_users:
        failure_reason_found = False
        ddb_records = aws_client.query_dynamodb_by_request_item(user.request_item)
        for record in ddb_records:
            if user.failed_reason != record.get('failedReason', {}).get('S'):
                continue
            else:
                assert user.failed_reason == record.get('failedReason', {}).get('S')
                failure_reason_found = True
                logger.info(f"Verified failure reason for {user.nhs_number}: {user.failed_reason}")
                save_evidence(record, f"{user.personalisation}/{user.failed_reason}.json")
                break
        assert failure_reason_found, f"Failure reason not found for {user.nhs_number}: {user.failed_reason}"
