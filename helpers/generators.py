import uuid
from .constants import API_ROUTING_CONFIGURATION_ALL_CHANNELS_CASCADE, NHS_NUMBER_SMOKE_TEST

class Generators():
    @staticmethod
    def generate_message_batch_body(scenario):
        return {
            "data": {
                "type": "MessageBatch",
                "attributes": {
                    "routingPlanId": API_ROUTING_CONFIGURATION_ALL_CHANNELS_CASCADE,
                    "messageBatchReference": str(uuid.uuid1()),
                    "messages": [
                        {
                            "messageReference": str(uuid.uuid1()),
                            "recipient": {
                                "nhsNumber": NHS_NUMBER_SMOKE_TEST
                            },
                            "personalisation": {
                                "exampleParameter": f"NHS Notify Release Test: {scenario}"
                            },
                            "originator": {
                                "odsCode": ""   
                            }
                        }
                    ]
                }
            }
        }

    @staticmethod
    def generate_message(user):
        return {
            "messageReference": user.message_reference,
            "recipient": {
                "nhsNumber": user.nhs_number,
                "contactDetails": {}
            },
            "personalisation": {
                "exampleParameter": user.personalisation
            },
            "originator": {
                "odsCode": ""
            }
        }

    @staticmethod
    def generate_alternative_contact_detail(user):
        return user.contact_detail

    @staticmethod
    def generate_single_message_body(scenario=None):
        return {
            "data": {
                "type": "Message",
                "attributes": {
                    "routingPlanId": API_ROUTING_CONFIGURATION_ALL_CHANNELS_CASCADE,
                    "messageReference": str(uuid.uuid1()),
                    "recipient": {
                        "nhsNumber": NHS_NUMBER_SMOKE_TEST
                    },
                    "personalisation": {
                        "exampleParameter": f"NHS Notify Release Test: {scenario}"
                    },
                    "originator": {
                        "odsCode": ""   
                    }   
                }
            }
        }
