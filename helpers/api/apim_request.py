import time
from helpers.generators import Generators
from helpers.test_data.batch_data import BatchData
from helpers.logger import get_logger

logger = get_logger(__name__)
class APIHelper:
    def __init__(self, client):
        self.client = client
        self.logger = get_logger(__name__)

    def send_single_message(self, body):
        response = self.client.post_single_message(body)
        assert response.status_code == 201
        return response

    def send_batch_message(self, body):
        response = self.client.post_batch_message(body)
        assert response.status_code == 201
        return response

    def get_message(self, message_id):
        response = self.client.get_message(message_id)
        assert response.status_code == 200
        return response

    def poll_for_message_status(self, message_id, expected_status, timeout_seconds=300):
        time.sleep(5)
        end_time = time.time() + timeout_seconds
        while time.time() < end_time:
            response = self.get_message(message_id)
            status = response.json()["data"]["attributes"]["messageStatus"]
            if status == expected_status:
                return status
            time.sleep(10)
        raise TimeoutError(f"Polling timeout. Final status: {status}")

    def get_nhsapp_account(self, params):
        response = self.client.get_nhsapp_account(params)
        assert response.status_code == 200
        return response

    def construct_batch_message_body(self, users):
        body = Generators.generate_message_batch_body("Message Batch")
        body['data']['attributes']['messages'] = [
            Generators.generate_message(user.nhs_number, user.message_reference)
            for user in users
        ]
        return body

    def send_and_verify_message_batch_request(self, body, test_users, poll_user):
        response = self.send_batch_message(body)
        assert response.status_code == 201
        message_items = response.json()['data']['attributes']['messages']
        logger.info("Batch message sent successfully")

        BatchData.update_request_items(test_users, message_items)
        self.poll_for_sending(BatchData.get_by_nhs_number(poll_user, test_users))
        logger.info("Messages are in a 'sending' state")

    def poll_for_sending(self, user):
        self.poll_for_message_status(
            user.request_item,
            'sending'
        )

    def poll_all_users_for_delivered(self, test_users):
        for user in test_users:
            try:
                self.poll_for_message_status(
                    user.request_item,
                    'delivered',
                    60
                )
                self.logger.info(f"REQUEST_ITEM#{user.request_item} is in a delivered state")
            except:
                raise AssertionError(f"REQUEST_ITEM#{user.request_item} is not in a delivered state")
    