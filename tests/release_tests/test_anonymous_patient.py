import uuid
from helpers.test_data.user_data import UserData
from helpers.aws.aws_client import AWSClient
from helpers.api.apim_request import APIHelper
from helpers.api.govuk_notify import verify_email_content

def test_anonymous_patient(api_client):
    api_helper = APIHelper(api_client)
    aws_client = AWSClient()

    test_user = [
        UserData(
            message_reference=str(uuid.uuid1()),
            communication_type="EMAIL",
            supplier="GOVUK_NOTIFY",
            personalisation="Anonymous Patient",
            contact_detail={
                "name": {
                    "prefix": "Ms",
                    "firstName": "Anon",
                    "middleNames": "Emus",
                    "lastName": "Patient",
                    "suffix": "BSc"
                },
                "email": "nhsnotify@anon.com"
            }
        )
    ]

    body = api_helper.construct_single_message_body(test_user[0])
    api_helper.send_and_verify_single_message_request(body, test_user[0])

    UserData.enrich_test_data(aws_client, test_user)

    verify_email_content(test_user[0])

    api_helper.poll_for_message_status(test_user[0].request_item, "delivered")
