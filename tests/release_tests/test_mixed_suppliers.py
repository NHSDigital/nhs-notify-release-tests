import uuid
from helpers.generators import Generators
from helpers.api.apim_request import send_batch_message, poll_for_message_status, get_message
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
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_batch_message(api_client):
    # Set up test data
    test_users = [
        BatchData(NHS_NUMBER_NHSAPP, str(uuid.uuid1()), "NHSAPP", "NHSAPP"),
        BatchData(NHS_NUMBER_EMAIL, str(uuid.uuid1()), "EMAIL", "GOVUK_NOTIFY"),
        BatchData(NHS_NUMBER_SMS, str(uuid.uuid1()), "SMS", "GOVUK_NOTIFY"),
        BatchData(NHS_NUMBER_GUKN_LETTER, str(uuid.uuid1()), "LETTER", "GOVUK_NOTIFY"),
        BatchData(NHS_NUMBER_MBA_LETTER, str(uuid.uuid1()), "LETTER", "MBA"),
        BatchData(NHS_NUMBER_SYNERTEC_LETTER, str(uuid.uuid1()), "LETTER", "SYNERTEC"),
        BatchData(NHS_NUMBER_PP_LETTER, str(uuid.uuid1()), "LETTER", "PRECISIONPROCO"),
    ]

    # Send request
    body = Generators.generate_message_batch_body("Message Batch")
    body['data']['attributes']['messages'] = [
        Generators.generate_message(user.nhs_number, user.message_reference)
        for user in test_users
    ]
    response = send_batch_message(api_client, body)
    assert response.status_code == 201
    logger.info("Sent message successfully")

    # Update test_users with request_item values in response
    message_items = response.json()['data']['attributes']['messages']
    logger.info(message_items)
    BatchData.update_request_items(test_users, message_items)

    # Wait until PP letter is in state of sending - usually the longest to process
    poll_for_message_status(
        api_client,
        BatchData.get_by_nhs_number(NHS_NUMBER_PP_LETTER, test_users).request_item,
        'sending'
        )
    logger.info("Messages are in a sending state")

    # Kick off test event on sftp lambdas to update status to delivered for sftp letters
    aws_client = AWSClient()
    aws_client.trigger_letters_polling_lambdas()
    logger.info("Letters should be in a delivered state")

    # Assert NHS App message recieved
    nhs_app_journey.nhs_app_login_and_view_message()

    # Assert GUKN Comms received - Need to provide client reference which is composed of <request_item>_<request_item_plan>_yyyy_mm_dd_1
    # Extract requestItemPlan from successful audit record
    for user in test_users:
        ddb_records = aws_client.query_dynamodb_by_request_item(user.request_item)
        for record in ddb_records:
            request_item_plan = record.get('communicationType',{}).get('S')
            if user.communication_type != request_item_plan:
                continue
            else:
                logger.info
                supplier = record.get('suppliers',{}).get('S')
                # Used for various letter suppliers
                if user.communication_type not in request_item_plan and user.supplier not in supplier:
                    continue
                else:
                    BatchData.update_request_item_plan_id(user, record.get('requestItemPlanId',{}).get('S'))
                    if user.communication_type == 'LETTER':
                        if user.supplier != 'GUKN':
                            ull = BatchData.update_batch_id(user, record.get('batchId',{}).get('S'))
                            logger.info(ull)
                        continue
                    else:
                        BatchData.update_contact_detail(user, record.get('recipientContactValue',{}).get('S'))

                    logger.info(f'Added record for {user.communication_type} {user.supplier} - {user.request_item_plan_id}')

    date = datetime.today().strftime('%Y-%m-%d')
    sms_gukn_id = f"{BatchData.get_by_nhs_number(NHS_NUMBER_SMS, test_users).request_item}_{BatchData.get_by_nhs_number(NHS_NUMBER_SMS, test_users).request_item_plan_id}_{date}_1"
    email_gukn_id = f"{BatchData.get_by_nhs_number(NHS_NUMBER_EMAIL, test_users).request_item}_{BatchData.get_by_nhs_number(NHS_NUMBER_EMAIL, test_users).request_item_plan_id}_{date}_1"
    letter_gukn_id = f"{BatchData.get_by_nhs_number(NHS_NUMBER_GUKN_LETTER, test_users).request_item}_{BatchData.get_by_nhs_number(NHS_NUMBER_GUKN_LETTER, test_users).request_item_plan_id}_{date}_1"
    logger.info(sms_gukn_id)

    # Query GUKN for record
    gukn_response = govuk_notify.get_message(sms_gukn_id)
    gukn_record = gukn_response['notifications'][0]
    assert gukn_record['body'] == f'NHS Notify Release Test: {BatchData.get_by_nhs_number(NHS_NUMBER_SMS, test_users).nhs_number}'
    assert gukn_record['phone_number'] == BatchData.get_by_nhs_number(NHS_NUMBER_SMS, test_users).contact_detail
    logger.info("SMS Appears as expected")
    
    gukn_response = govuk_notify.get_message(email_gukn_id)
    gukn_record = gukn_response['notifications'][0]
    assert gukn_record['body'] == f'NHS Notify Release Test: {BatchData.get_by_nhs_number(NHS_NUMBER_EMAIL, test_users).nhs_number}'
    assert gukn_record['email_address'] == BatchData.get_by_nhs_number(NHS_NUMBER_EMAIL, test_users).contact_detail
    logger.info("Email Appears as expected")
    
    #Unable to verify content
    gukn_response = govuk_notify.get_message(letter_gukn_id)
    id = gukn_response['notifications'][0]['id']
    govuk_notify.get_pdf(id)
    assert os.path.exists('tests/evidence/gukn_letter.pdf')
    logger.info("Letter pdf exists")

    # Assert SFTP csvs are in expected location

    # S3 Bucket that contains letter supplier csvs
    bucket_name = "comms-736102632839-eu-west-2-uat-api-lspl-letter-csv"
    # Paths to the letter supplier csv locations
 
    pp = f"PRECISIONPROCO/uploaded/pp-release-testing/{BatchData.get_by_nhs_number(NHS_NUMBER_PP_LETTER, test_users).batch_id}.csv" 
    mba = f"MBA/uploaded/hh-release-testing/{BatchData.get_by_nhs_number(NHS_NUMBER_MBA_LETTER, test_users).batch_id}.csv"
    syn = f"SYNERTEC/uploaded/synertec-release-testing/{BatchData.get_by_nhs_number(NHS_NUMBER_SYNERTEC_LETTER, test_users).batch_id}.csv"
    # On request item plan for a successful channel request item should have batchId field in dynamo will contain the file name    
    # Iterate over available letter supplier locations and assert that available csvs contain expected content

    pp_content = aws_client.get_s3_object(bucket_name, pp)
    assert BatchData.get_by_nhs_number(NHS_NUMBER_PP_LETTER, test_users).nhs_number in pp_content
    mba_content = aws_client.get_s3_object(bucket_name, mba)
    assert BatchData.get_by_nhs_number(NHS_NUMBER_MBA_LETTER, test_users).nhs_number in mba_content
    syn_content = aws_client.get_s3_object(bucket_name, syn)
    assert BatchData.get_by_nhs_number(NHS_NUMBER_SYNERTEC_LETTER, test_users).nhs_number in syn_content
    logger.info("SFTP letters appear as expected")

    # Assert Dynamo records
    for user in test_users:
        try:
            poll_for_message_status(
                api_client,
                user.request_item,
                'delivered',
                30
            )
            logger.info(f"REQUEST_ITEM#{user.request_item} is in a delivered state")
        except:
            raise AssertionError(f"REQUEST_ITEM#{user.request_item} is not in a delivered state")
