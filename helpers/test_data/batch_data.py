from typing import List, Optional


class BatchData:
    def __init__(self, nhs_number: str, message_reference: str, communication_type: str, supplier: str):
        self.nhs_number = nhs_number
        self.message_reference = message_reference
        self.communication_type = communication_type
        self.supplier = supplier
        self.request_item = None
        self.request_item_plan_id = None
        self.batch_id = None
        self.contact_detail = None

    @staticmethod
    def get_by_nhs_number(nhs_number: str, test_users: List["BatchData"]) -> Optional["BatchData"]:
        return next((u for u in test_users if u.nhs_number == nhs_number), None)

    @staticmethod
    def update_request_items(test_users: List["BatchData"], response_messages: List[dict]) -> None:
        reference_map = {msg['messageReference']: msg['id'] for msg in response_messages}
        for user in test_users:
            user.request_item = reference_map.get(user.message_reference)
    
    @staticmethod
    def update_request_item_plan_id(user, request_item_plan_id):
        user.request_item_plan_id = request_item_plan_id
    
    @staticmethod
    def update_batch_id(user, batch_id):
        user.batch_id = batch_id
    
    @staticmethod
    def update_contact_detail(user, contact_detail):
        user.contact_detail = contact_detail

    def __repr__(self):
        return (
            f"BatchData(nhs_number='{self.nhs_number}', "
            f"message_reference='{self.message_reference}', "
            f"communication_type='{self.communication_type}', "
            f"supplier='{self.supplier}', "
            f"batch_id='{self.address}', "
            f"contact_detail='{self.contact_detail}', "
            f"request_item='{self.request_item}', "
            f"request_item_plan_id='{self.request_item_plan_id}')"
        )
    