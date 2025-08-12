from typing import List, Optional
from datetime import datetime
from helpers.logger import get_logger

logger = get_logger(__name__)

class UserData:
    def __init__(
        self,
        nhs_number,
        message_reference=None,
        communication_type=None,
        supplier=None,
        personalisation=None,
        request_item=None,
        request_item_plan_id=None,
        batch_id=None,
        gukn_id=None,
        contact_detail=None,
        ods_code=None
    ):
        self.nhs_number = nhs_number
        self.message_reference = message_reference
        self.communication_type = communication_type
        self.supplier = supplier
        self.personalisation = personalisation
        self.request_item = request_item
        self.request_item_plan_id = request_item_plan_id
        self.batch_id = batch_id
        self.gukn_id = gukn_id
        self.contact_detail = contact_detail
        self.ods_code = ods_code

    @staticmethod
    def get_by_nhs_number(nhs_number: str, test_users: List["UserData"]) -> Optional["UserData"]:
        return next((u for u in test_users if u.nhs_number == nhs_number), None)

    @staticmethod
    def update_request_items(test_users: List["UserData"], response_messages: List[dict]) -> None:
        reference_map = {msg['messageReference']: msg['id'] for msg in response_messages}
        for user in test_users:
            user.request_item = reference_map.get(user.message_reference)
    
    @staticmethod
    def update_request_item(user, request_item):
        user.request_item = request_item
    
    @staticmethod
    def update_request_item_plan_id(user, request_item_plan_id):
        user.request_item_plan_id = request_item_plan_id
    
    @staticmethod
    def update_batch_id(user, batch_id):
        user.batch_id = batch_id
        
    @staticmethod
    def update_ods_code(user, ods_code):
        user.ods_code = ods_code

    @staticmethod
    def update_gukn_id(test_users):
        date = datetime.today().strftime('%Y-%m-%d')
        for user in test_users:
            user.gukn_id = f"{user.request_item}_{user.request_item_plan_id}_{date}_1"
    
    @staticmethod
    def update_contact_detail(user, contact_detail):
        user.contact_detail = contact_detail
        
    @staticmethod
    def enrich_test_data(aws_client, test_users):
        for user in test_users:
            ddb_records = aws_client.query_dynamodb_by_request_item(user.request_item)
            for record in ddb_records:
                request_item_plan = record.get('communicationType',{}).get('S')
                if user.communication_type != request_item_plan:
                    continue
                else:
                    supplier = record.get('suppliers',{}).get('S')
                    # Used for various letter suppliers
                    if user.communication_type not in request_item_plan and user.supplier not in supplier:
                        continue
                    else:
                        UserData.update_request_item_plan_id(user, record.get('requestItemPlanId',{}).get('S'))
                        if user.communication_type == 'LETTER':
                            if user.supplier != 'GUKN':
                                UserData.update_batch_id(user, record.get('batchId',{}).get('S'))
                            continue
                        else:
                            UserData.update_contact_detail(user, record.get('recipientContactValue',{}).get('S'))
        UserData.update_gukn_id(test_users)

    def __repr__(self):
        return (
            f"UserData(nhs_number='{self.nhs_number}', "
            f"message_reference='{self.message_reference}', "
            f"communication_type='{self.communication_type}', "
            f"supplier='{self.supplier}', "
            f"personalisation='{self.personalisation}', "
            f"batch_id='{self.batch_id}', "
            f"gukn_id='{self.gukn_id}', "
            f"contact_detail='{self.contact_detail}', "
            f"request_item='{self.request_item}', "
            f"request_item_plan_id='{self.request_item_plan_id}', "
            f"ods_code='{self.ods_code}')"
        )
    