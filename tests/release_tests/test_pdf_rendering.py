import uuid
from helpers.constants import NHS_NUMBER_GUKN_LETTER, PDF_RENDERING_ROUTING_CONFIGURATION
from helpers.api.apim_request import APIHelper
from helpers.aws.aws_client import AWSClient
from helpers.test_data.user_data import UserData
from helpers import switch_account
def test_pdf_rendering(api_client):
    api_helper = APIHelper(api_client)
    aws_client = AWSClient()

    user = UserData(
        nhs_number = NHS_NUMBER_GUKN_LETTER,
        routing_plan_id=PDF_RENDERING_ROUTING_CONFIGURATION,
        message_reference= str(uuid.uuid1()),
        personalisation = "PDF Rendering"
    )

    body = api_helper.construct_single_message_body(user)
    api_helper.send_and_verify_single_message_request(body, user)
    
    aws_client.verify_pdf_rendering_letter_test_account(user)
    switch_account.switch_aws_account()
    aws_client.verify_pdf_rendering_letter_mgmt_account(user)    
    api_helper.poll_for_message_status(user.request_item, "sending")
