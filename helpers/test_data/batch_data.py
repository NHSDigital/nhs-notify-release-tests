from typing import List, Optional


class BatchData:
    def __init__(self, nhs_number: str, message_reference: str, personalisation: str):
        self.nhs_number = nhs_number
        self.message_reference = message_reference
        self.personalisation = personalisation
        self.request_item = None


    @staticmethod
    def get_by_nhs_number(nhs_number: str, test_users: List["BatchData"]) -> Optional["BatchData"]:
        return next((u for u in test_users if u.nhs_number == nhs_number), None)

    @staticmethod
    def update_request_items(test_users: List["BatchData"], response_messages: List[dict]) -> None:
        reference_map = {msg['messageReference']: msg['id'] for msg in response_messages}
        for user in test_users:
            user.request_item = reference_map.get(user.message_reference)

    def __repr__(self):
        return (
            f"BatchData(nhs_number='{self.nhs_number}', "
            f"message_reference='{self.message_reference}', "
            f"personalisation='{self.personalisation}', "
            f"request_item='{self.request_item}')"
        )
        
