import time
from helpers.generators import Generators
from helpers.test_data.user_data import UserData
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

    def get_nhsapp_account(self, params):
        response = self.client.get_nhsapp_account(params)
        assert response.status_code == 200
        return response

    def construct_batch_message_body(self, users):
        body = Generators.generate_message_batch_body("Message Batch")
        messages = []
        for user in users:
            message = Generators.generate_message(user)
            if user.nhs_number is not None:
                message['recipient']['nhsNumber'] = user.nhs_number
            else:
                message['recipient'].pop('nhsNumber')
            if user.ods_code is not None:
                message['originator']['odsCode'] = user.ods_code
            else:
                message['originator'].pop('odsCode')
            if user.contact_detail:
                message['recipient']['contactDetails'] = user.contact_detail
            messages.append(message)
        body['data']['attributes']['messages'] = messages
        return body

    def construct_single_message_body(self, user):
        body = Generators.generate_single_message_body()
        body['data']['attributes']['messageReference'] = user.message_reference
        body['data']['attributes']['personalisation']['exampleParameter'] = user.personalisation
        if user.nhs_number is not None:
            body['data']['attributes']['recipient']['nhsNumber'] = user.nhs_number
        else:
            body['data']['attributes']['recipient'].pop('nhsNumber')
        if user.ods_code is not None:
            body['data']['attributes']['originator']['odsCode'] = user.ods_code
        else:
            body['data']['attributes']['originator'].pop('odsCode')
        if user.contact_detail:
            body['data']['attributes']['recipient']['contactDetails'] = user.contact_detail
        return body

    def send_and_verify_message_batch_request(self, body, test_users, poll_user, status='sending'):
        response = self.send_batch_message(body)
        assert response.status_code == 201
        message_items = response.json()['data']['attributes']['messages']
        logger.info("Batch message sent successfully")

        UserData.update_request_items(test_users, message_items)
        self.poll_for_message_status(UserData.get_by_nhs_number(poll_user, test_users).request_item, status)
        logger.info(f"Messages are in a '{status}' state")
    
    def send_and_verify_single_message_request(self, body, user, status='sending'):
        response = self.send_single_message(body)
        assert response.status_code == 201
        request_id = response.json()['data']['id']
        logger.info("Single message sent successfully")

        UserData.update_request_item(user, request_id)
        self.poll_for_message_status(request_id, status)
        logger.info(f"Message is in a '{status}' state")

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
