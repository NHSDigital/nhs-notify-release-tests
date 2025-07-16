from helpers.generators import Generators
from helpers.api.apim_request import send_batch_message, get_message, get_nhsapp_account
from helpers.constants import NHS_NUMBER_NHSAPP, NHS_NUMBER_EMAIL, NHS_NUMBER_SMS, NHS_NUMBER_GUKN_LETTER, \
    NHS_NUMBER_MBA_LETTER, NHS_NUMBER_SYNERTEC_LETTER, NHS_NUMBER_PP_LETTER
import uuid
from helpers.test_data.batch_data import BatchData

def test_single_message(api_client):
    test_users = [
        BatchData(NHS_NUMBER_NHSAPP,str(uuid.uuid1()),"NHS App"),
        BatchData(NHS_NUMBER_EMAIL,str(uuid.uuid1()),"Email"),
        BatchData(NHS_NUMBER_SMS,str(uuid.uuid1()),"SMS"),
        BatchData(NHS_NUMBER_GUKN_LETTER,str(uuid.uuid1()),"GUKN Letter"),
        BatchData(NHS_NUMBER_MBA_LETTER,str(uuid.uuid1()),"MBA Letter"),
        BatchData(NHS_NUMBER_SYNERTEC_LETTER,str(uuid.uuid1()),"Synetec Letter"),
        BatchData(NHS_NUMBER_PP_LETTER,str(uuid.uuid1()),"Precision Proco Letter"),
    ]

    body = Generators.generate_message_batch_body('Message Batch')
    body['data']['attributes']['messages'] = []
    for user in test_users:
        body['data']['attributes']['messages'].append(
            Generators.generate_message(
                user.nhs_number,
                user.message_reference,
                user.personalisation
            )
        )

    response = send_batch_message(api_client, body)
    assert response.status_code == 201

    resp = response.json()
    message_request_items = resp.get('data').get('attributes').get('messages')

    message_reference_to_id = {msg['messageReference']: msg['id'] for msg in message_request_items}

    for user in test_users:
        user.request_item = message_reference_to_id.get(user.message_reference)

    summary = [
        {
            'nhs_number': user.nhs_number,
            'message_reference': user.message_reference,
            'personalisation': user.personalisation,
            'request_item': user.request_item
        }
        for user in test_users
    ]

    raise AssertionError(summary)