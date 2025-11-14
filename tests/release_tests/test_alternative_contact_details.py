import uuid
from helpers.test_data.user_data import UserData
from helpers.aws.aws_client import AWSClient
from helpers.api.apim_request import APIHelper
from helpers.api.govuk_notify import verify_email_content, verify_sms_content, verify_gukn_letter
from helpers.constants import (
    NHS_NUMBER_EMAIL,
    NHS_NUMBER_SMS,
    NHS_NUMBER_GUKN_LETTER
)
from helpers.logger import get_logger

logger = get_logger(__name__)

def test_alternative_contact_details(api_client):
    api_helper = APIHelper(api_client)
    aws_client = AWSClient()

    test_users = [
        UserData(
            nhs_number=NHS_NUMBER_EMAIL,
            message_reference=str(uuid.uuid1()),
            communication_type="EMAIL",
            supplier="GOVUK_NOTIFY",
            personalisation="Alternative Contact Details",
            contact_detail={
                "email": "nhsnotify@acd.com"
            }
        ),
        UserData(
            nhs_number=NHS_NUMBER_SMS,
            message_reference=str(uuid.uuid1()),
            communication_type="SMS",
            supplier="GOVUK_NOTIFY",
            personalisation="Alternative Contact Details",
            contact_detail={
                "sms": "07777777777"
            }
        ),
        UserData(
            nhs_number=NHS_NUMBER_GUKN_LETTER,
            message_reference=str(uuid.uuid1()),
            communication_type="LETTER",
            supplier="GOVUK_NOTIFY",
            personalisation="Alternative Contact Details",
            contact_detail= {
                "address": {
                    "lines": [
                        "1 Street",
                        "Town",
                        "City"
                    ],
                    "postcode": "LS10 1EL"
                }
            }
        )
    ]

    body = api_helper.construct_batch_message_body(test_users)
    api_helper.send_and_verify_message_batch_request(body, test_users)

    UserData.enrich_test_data(aws_client, test_users)

    verify_email_content(UserData.get_by_nhs_number(NHS_NUMBER_EMAIL, test_users))
    verify_sms_content(UserData.get_by_nhs_number(NHS_NUMBER_SMS, test_users))
    verify_gukn_letter(UserData.get_by_nhs_number(NHS_NUMBER_GUKN_LETTER, test_users))
