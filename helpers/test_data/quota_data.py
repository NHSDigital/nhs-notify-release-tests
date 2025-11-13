from helpers.constants import get_client
from helpers.logger import get_logger

logger = get_logger(__name__)

class QuotaData:
    def __init__(
        self,
        supplier=None,
        communication_type=None,
        client_id=None,
        campaign_id="release_testing",
    ):
        self.supplier = supplier
        self.communication_type = communication_type
        self.client_id = client_id
        self.campaign_id = campaign_id
    
    def update_supplier(self, supplier):
        self.supplier = supplier

    def update_communication_type(self, communication_type):
        self.communication_type = communication_type

    def update_client_id(self, client_id):
        self.client_id = client_id

    def update_campaign_id(self, campaign_id):
        self.campaign_id = campaign_id

