import uuid
import csv
from dataclasses import asdict, is_dataclass
from typing import List, Union
from .constants import API_ROUTING_CONFIGURATION_ALL_CHANNELS_CASCADE, NHS_NUMBER_SMOKE_TEST, CSV_HEADERS

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

    @staticmethod
    def generate_mesh_csv(users: List[Union[dict, object]], file_path: str):
        rows = []

        for user in users:
            data = Generators._object_to_dict(user)
            row = Generators._map_user_to_csv_row(data)
            rows.append(row)

        with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _object_to_dict(obj):
        if is_dataclass(obj):
            return asdict(obj)
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        elif isinstance(obj, dict):
            return obj
        else:
            raise TypeError("User must be a dataclass, have __dict__, or be a dict.")

    @staticmethod
    def _map_user_to_csv_row(data: dict) -> dict:
        get = lambda key, default="": data.get(key, default)

        contact = get("contact_detail", {}) or {}
        address = contact.get("address", {}) or {}
        address_lines = address.get("lines", ["", "", ""])
        while len(address_lines) < 3:
            address_lines.append("") 

        personalisation = get("personalisation", "")
        personalisation_value = str(personalisation)

        return {
            "requestItemRefId": get("message_reference", ""),
            "nhsNumber": get("nhs_number", ""),
            "personalisation_exampleParameter": personalisation_value,
            "originator_odsCode": get("ods_code", ""),
            "recipient_contactDetails_email": contact.get("email", ""),
            "recipient_contactDetails_sms": contact.get("sms", ""),
            "recipient_contactDetails_address_lines1": address_lines[0],
            "recipient_contactDetails_address_lines2": address_lines[1],
            "recipient_contactDetails_address_lines3": address_lines[2],
            "recipient_contactDetails_address_postcode": address.get("postcode", ""),
        }
