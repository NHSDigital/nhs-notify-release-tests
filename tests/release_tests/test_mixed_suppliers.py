import uuid
from helpers.generators import Generators
from helpers.api.apim_request import send_batch_message, poll_for_message_status
from helpers.constants import (
    NHS_NUMBER_NHSAPP,
    NHS_NUMBER_EMAIL,
    NHS_NUMBER_SMS,
    NHS_NUMBER_GUKN_LETTER,
    NHS_NUMBER_MBA_LETTER,
    NHS_NUMBER_SYNERTEC_LETTER,
    NHS_NUMBER_PP_LETTER,
)
from helpers.test_data.batch_data import BatchData
from helpers.aws.aws_client import AWSClient
from helpers.api import govuk_notify
from helpers.ui import nhs_app_journey

def test_batch_message(api_client):
    #raise AssertionError(govuk_notify.get_message())
    # Set up test data
    test_users = [
        BatchData(NHS_NUMBER_NHSAPP, str(uuid.uuid1()), "NHS App"),
        BatchData(NHS_NUMBER_EMAIL, str(uuid.uuid1()), "Email"),
        BatchData(NHS_NUMBER_SMS, str(uuid.uuid1()), "SMS"),
        BatchData(NHS_NUMBER_GUKN_LETTER, str(uuid.uuid1()), "GUKN Letter"),
        BatchData(NHS_NUMBER_MBA_LETTER, str(uuid.uuid1()), "MBA Letter"),
        BatchData(NHS_NUMBER_SYNERTEC_LETTER, str(uuid.uuid1()), "Synetec Letter"),
        BatchData(NHS_NUMBER_PP_LETTER, str(uuid.uuid1()), "Precision Proco Letter"),
    ]

    # Send request
    body = Generators.generate_message_batch_body("Message Batch")
    body['data']['attributes']['messages'] = [
        Generators.generate_message(user.nhs_number, user.message_reference, user.personalisation)
        for user in test_users
    ]
    response = send_batch_message(api_client, body)
    assert response.status_code == 201

    # Update test_users with request_item values in response
    response_json = response.json()
    message_items = response_json['data']['attributes']['messages']
    BatchData.update_request_items(test_users, message_items)

    # Wait until PP letter is in state of sending - usually the longest to process
    poll_for_message_status(
        api_client,
        BatchData.get_by_nhs_number(NHS_NUMBER_PP_LETTER, test_users).request_item,
        'sending'
        )

    # Kick off test event on sftp lambdas to update status to delivered for sftp letters
    aws_client = AWSClient()
    aws_client.trigger_lambda('comms-uat-api-nsp-letters-notify-polling')
    aws_client.trigger_lambda('comms-uat-api-lspl-sftppoll')
    aws_client.trigger_lambda('comms-uat-letters-api-lss-sftppollsynertec')
    aws_client.trigger_lambda('comms-uat-api-lspp-sftppollprecisionproco')

    # Assert NHS App message recieved
    nhs_app_journey.nhs_app_login_and_view_message()

    # Assert GUKN Comms received
    # Need to provide client reference which is composed of <request_item>_<request_item_plan>_yyyy_mm_dd_1
    # govuk_notify.get_gukn_message()

    # Assert SFTP csvs are in expected location

    # Assert Dynamo records

