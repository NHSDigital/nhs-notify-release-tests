class BatchData():
    def __init__(self, nhs_number: str, message_reference: str, personalisation: str):
        self.nhs_number = nhs_number
        self.message_reference = message_reference
        self.personalisation = personalisation
        self.request_item = None