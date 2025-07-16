from helpers.api.apim_request import send_single_message, get_message, poll_for_message_status
from helpers.aws.aws_client import AWSClient
from helpers.generators import Generators
from helpers.constants import NHS_NUMBER_GUKN_LETTER

def test_filter_rules(api_client):
    # Enable filter rule for letters to prevent letter requests from being processed
    aws_client = AWSClient()
    aws_client.filter_rules(enabled=True)
    
    # Set body of the request to target user with only letter channel available
    body = Generators.generate_single_message_body("Filter rules")
    body["data"]["attributes"]["recipient"]["nhsNumber"] = NHS_NUMBER_GUKN_LETTER

    # Send request and verify it ends in a failed state
    response = send_single_message(api_client, body)
    message_id = response.json().get('data').get('id')
    poll_for_message_status(api_client, message_id, 'failed')

    # Verify request has expected channel status and description
    get_response = get_message(api_client, message_id)
    channels = get_response.json().get('data').get('attributes').get('channels')
    for channel in channels:
        if channel.get('type') == 'letter':
            assert channel.get('channelStatus') == 'failed'
            assert channel.get('channelStatusDescription') == 'Failed reason: Matched exclusion rule with ID NHS Notify Automated Release Regression'

    # Disable filter rule
    aws_client.filter_rules(enabled=False)