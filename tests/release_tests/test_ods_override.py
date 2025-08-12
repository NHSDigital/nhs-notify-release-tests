import uuid
from helpers.constants import NHS_NUMBER_NHSAPP
from helpers.api.apim_request import APIHelper
from helpers.test_data.user_data import UserData
from helpers.ui import nhs_app_journey

def test_ods_override(api_client):
    api_helper = APIHelper(api_client)
    
    user = UserData(
        nhs_number = NHS_NUMBER_NHSAPP,
        message_reference= str(uuid.uuid1()),
        ods_code = "Y51",
        personalisation = "Y51 ODS Override"
    )

    body = api_helper.construct_single_message_body(user)
    api_helper.send_and_verify_single_message_request(body, user)
    
    nhs_app_journey.nhs_app_login_and_view_message("THE NORTH MIDLANDS AND EAST PROGRAMME FOR IT (NMEPFIT)", user.personalisation)
    
    api_helper.poll_for_message_status(user.request_item, "delivered")
