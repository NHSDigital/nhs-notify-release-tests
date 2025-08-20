import uuid
from helpers.test_data.user_data import UserData
from helpers.aws.aws_client import AWSClient
from helpers.api.apim_request import APIHelper
from helpers.api.govuk_notify import verify_email_content, verify_sms_content, verify_gukn_letter
from helpers.ui import nhs_app_journey
from helpers.constants import (
    NHS_NUMBER_NHSAPP,
    NHS_NUMBER_EMAIL,
    NHS_NUMBER_SMS,
    NHS_NUMBER_GUKN_LETTER,
    NHS_NUMBER_MBA_LETTER,
    NHS_NUMBER_SYNERTEC_LETTER,
    NHS_NUMBER_PP_LETTER,
)

def test_batch_message(api_client):
    api_helper = APIHelper(api_client)
    aws_client = AWSClient()

    # Set up test data
    test_users = [
        UserData(NHS_NUMBER_NHSAPP, str(uuid.uuid1()), "NHSAPP", "NHSAPP", personalisation="Mixed Suppliers Message Batch"),
        UserData(NHS_NUMBER_EMAIL, str(uuid.uuid1()), "EMAIL", "GOVUK_NOTIFY", personalisation="Mixed Suppliers Message Batch"),
        UserData(NHS_NUMBER_SMS, str(uuid.uuid1()), "SMS", "GOVUK_NOTIFY", personalisation="Mixed Suppliers Message Batch"),
        UserData(NHS_NUMBER_GUKN_LETTER, str(uuid.uuid1()), "LETTER", "GOVUK_NOTIFY", personalisation="Mixed Suppliers Message Batch"),
        UserData(NHS_NUMBER_MBA_LETTER, str(uuid.uuid1()), "LETTER", "MBA", personalisation="Mixed Suppliers Message Batch"),
        UserData(NHS_NUMBER_SYNERTEC_LETTER, str(uuid.uuid1()), "LETTER", "SYNERTEC", personalisation="Mixed Suppliers Message Batch"),
        UserData(NHS_NUMBER_PP_LETTER, str(uuid.uuid1()), "LETTER", "PRECISIONPROCO", personalisation="Mixed Suppliers Message Batch"),
    ]

    body = api_helper.construct_batch_message_body(test_users)
    api_helper.send_and_verify_message_batch_request(body, test_users, NHS_NUMBER_PP_LETTER)

    nhs_app_journey.nhs_app_login_and_view_message(
        personalisation=UserData.get_by_nhs_number(NHS_NUMBER_NHSAPP, test_users).personalisation)

    aws_client.trigger_letters_polling_lambdas()

    UserData.enrich_test_data(aws_client, test_users)

    verify_email_content(UserData.get_by_nhs_number(NHS_NUMBER_EMAIL, test_users))
    verify_sms_content(UserData.get_by_nhs_number(NHS_NUMBER_SMS, test_users))
    verify_gukn_letter(UserData.get_by_nhs_number(NHS_NUMBER_GUKN_LETTER, test_users))
    aws_client.verify_mba_letter(UserData.get_by_nhs_number(NHS_NUMBER_MBA_LETTER, test_users))
    aws_client.verify_synertec_letter(UserData.get_by_nhs_number(NHS_NUMBER_SYNERTEC_LETTER, test_users))
    aws_client.verify_precision_proco_letter(UserData.get_by_nhs_number(NHS_NUMBER_PP_LETTER, test_users))

    api_helper.poll_all_users_for_delivered(test_users)
