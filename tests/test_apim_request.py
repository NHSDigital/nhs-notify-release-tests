from helpers.generators import Generators
from helpers.api.apim_request import send_single_message, send_batch_message, get_message, get_nhsapp_account


def test_single_message(api_client):
    body = Generators.generate_single_message_body("single message smoke test")
    response = send_single_message(api_client, body)
    assert response.status_code == 201

def test_batch_message(api_client):
    body = Generators.generate_message_batch_body("batch message smoke test")
    response = send_batch_message(api_client,body)
    assert response.status_code == 201

def test_get_message(api_client):
    body = Generators.generate_single_message_body("get request message smoke test")
    post_response = send_single_message(api_client, body)

    message_id = post_response.json().get("data").get("id")
    response = get_message(api_client, message_id)

    assert response.status_code == 200

def test_nhsapp_account(api_client):
    response = get_nhsapp_account(
        api_client,
        {
            "ods-organisation-code": "X26",
            "page": 1
        }
    )

    assert response.status_code == 200