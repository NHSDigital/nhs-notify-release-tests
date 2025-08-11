from typing import List, Optional
from datetime import datetime
from helpers.logger import get_logger

logger = get_logger(__name__)

class BatchData:
    def __init__(self, nhs_number: str, message_reference: str, communication_type: str, supplier: str):
        self.nhs_number = nhs_number
        self.message_reference = message_reference
        self.communication_type = communication_type
        self.supplier = supplier
        self.request_item = None
        self.request_item_plan_id = None
        self.batch_id = None
        self.gukn_id = None
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
                        BatchData.update_request_item_plan_id(user, record.get('requestItemPlanId',{}).get('S'))
                        if user.communication_type == 'LETTER':
                            if user.supplier != 'GUKN':
                                BatchData.update_batch_id(user, record.get('batchId',{}).get('S'))
                            continue
                        else:
                            BatchData.update_contact_detail(user, record.get('recipientContactValue',{}).get('S'))
        BatchData.update_gukn_id(test_users)

    def __repr__(self):
        return (
            f"BatchData(nhs_number='{self.nhs_number}', "
            f"message_reference='{self.message_reference}', "
            f"communication_type='{self.communication_type}', "
            f"supplier='{self.supplier}', "
            f"batch_id='{self.batch_id}', "
            f"gukn_id='{self.gukn_id}', "
            f"contact_detail='{self.contact_detail}', "
            f"request_item='{self.request_item}', "
            f"request_item_plan_id='{self.request_item_plan_id}')"
        )
    