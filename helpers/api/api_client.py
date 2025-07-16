import requests

class ApiClient:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def post_single_message(self, body):
        return requests.post(f"{self.url}/v1/messages", headers=self.headers, json=body)

    def post_batch_message(self, body):
        return requests.post(f"{self.url}/v1/message-batches", headers=self.headers, json=body)

    def get_message(self, message_id):
        return requests.get(f"{self.url}/v1/messages/{message_id}", headers=self.headers)

    def get_nhsapp_account(self, parameters):
        return requests.get(f"{self.url}/channels/nhsapp/accounts", headers=self.headers, params=parameters)