import time

def send_single_message(client, body):
    response = client.post_single_message(body)
    assert response.status_code == 201
    return response

def send_batch_message(client, body):
    response = client.post_batch_message(body)
    assert response.status_code == 201
    return response

def get_message(client, message_id):
    response = client.get_message(message_id)
    assert response.status_code == 200
    return response

def poll_for_message_status(client, message_id, expected_status, timeout_seconds=300):
    time.sleep(10)
    end_time = time.time() + timeout_seconds
    while time.time() < end_time:
        response = get_message(client, message_id)
        status = response.json()["data"]["attributes"]["messageStatus"]
        if status == expected_status:
            return status
        time.sleep(10)
    raise TimeoutError(f"Polling timeout. Final status: {status}")

def get_nhsapp_account(client, params):
    response = client.get_nhsapp_account(params)
    assert response.status_code == 200
    return response