import uuid
from helpers.api.apim_request import APIHelper
from helpers.aws.aws_client import AWSClient
from helpers.test_data.user_data import UserData
from helpers.constants import NHS_NUMBER_GUKN_LETTER
from helpers.evidence import store_evidence_to_json_file

def test_filter_rules(api_client):
    api_helper = APIHelper(api_client)
    aws_client = AWSClient()

    aws_client.filter_rules(enabled=True)

    user = [
        UserData(
            nhs_number = NHS_NUMBER_GUKN_LETTER,
            personalisation = "Filter Rule",
            message_reference= str(uuid.uuid1()),
        )
    ]    

    body = api_helper.construct_single_message_body(user[0])
    api_helper.send_and_verify_single_message_request(body, user[0], 'failed')

    get_response = api_helper.get_message(user[0].request_item)
    channels = get_response.json().get('data').get('attributes').get('channels')
    for channel in channels:
        if channel.get('type') == 'letter':
            assert channel.get('channelStatus') == 'failed'
            assert channel.get('channelStatusDescription') == 'Failed reason: Matched exclusion rule with ID NHS Notify Automated Release Regression'
    store_evidence_to_json_file(get_response.json(), f"{user[0].personalisation}/filter_rule_response.json")

    aws_client.filter_rules(enabled=False)