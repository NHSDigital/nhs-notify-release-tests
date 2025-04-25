from helpers.generators import Generators

def test_single_message(api_client):
    body = Generators.generate_single_message_body("single message smoke test")
    response = api_client.post_single_message(body)
    assert response.status_code == 201

def test_batch_message(api_client):
    body = Generators.generate_message_batch_body("batch message smoke test")
    response = api_client.post_batch_message(body)
    assert response.status_code == 201

def test_get_message(api_client):
    body = Generators.generate_single_message_body("get request message smoke test")
    post_response = api_client.post_single_message(body)

    message_id = post_response.json().get("data").get("id")
    response = api_client.get_message(message_id)

    assert response.status_code == 200

def test_nhsapp_account(api_client):
    response = api_client.get_nhsapp_account(
        {
            "ods-organisation-code": "X26",
            "page": 1
        }
    )

    assert response.status_code == 200