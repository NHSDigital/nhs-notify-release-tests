import uuid
import os
from helpers.bash import bash_command
from helpers.test_data.user_data import UserData
from helpers.aws.aws_client import AWSClient
from helpers.api.apim_request import APIHelper
from helpers.api.govuk_notify import verify_email_content, verify_sms_content
from helpers.generators import Generators
from helpers.mesh.mesh_helper import MeshHelper
from helpers.ui import nhs_app_journey
from helpers.constants import (
    NHS_NUMBER_NHSAPP,
    NHS_NUMBER_EMAIL,
    NHS_NUMBER_SMS,
    NHS_NUMBER_MBA_LETTER,
    NHS_NUMBER_SYNERTEC_LETTER,
    NHS_NUMBER_PP_LETTER,
    get_env
)

def test_mesh(api_client):
    bash_command("scripts/get_mesh_cli.sh")
    bash_command("source .venv/bin/activate")

    api_helper = APIHelper(api_client)
    aws_client = AWSClient()
    mesh_helper = MeshHelper()

    test_users = [
        UserData(
            nhs_number=NHS_NUMBER_NHSAPP,
            message_reference=str(uuid.uuid4()),
            communication_type="NHSAPP",
            supplier="NHSAPP",
            personalisation="Mesh - Mixed Suppliers",
            ods_code="Y51"
        ),
        UserData(
            nhs_number=NHS_NUMBER_EMAIL,
            message_reference=str(uuid.uuid4()),
            communication_type="EMAIL",
            supplier="GOVUK_NOTIFY",
            personalisation="Mesh - Mixed Suppliers", 
            contact_detail={"email": "test@example.com"}
        ),
        UserData(
            nhs_number=NHS_NUMBER_SMS,
            message_reference=str(uuid.uuid4()),
            communication_type="SMS",
            supplier="GOVUK_NOTIFY",
            personalisation="Mesh - Mixed Suppliers",
            contact_detail={"sms": "07123456789"}
        ),
        UserData(
            nhs_number=NHS_NUMBER_MBA_LETTER,
            message_reference=str(uuid.uuid4()),
            communication_type="LETTER",
            supplier="MBA",
            personalisation="Mesh - Mixed Suppliers",
            contact_detail={
                "address": {
                    "lines": [
                        "1 Street",
                        "Town",
                        "City"
                    ],
                    "postcode": "LS10 1EL"
                }
            }
        ),
        UserData(
            nhs_number=NHS_NUMBER_SYNERTEC_LETTER,
            message_reference=str(uuid.uuid4()),
            communication_type="LETTER",
            supplier="SYNERTEC",
            personalisation="Mesh - Mixed Suppliers",
            contact_detail={
                "address": {
                    "lines": [
                        "2 Street",
                        "Town",
                        "City"
                    ],
                    "postcode": "LS10 1EL"
                }
            }
        ),
        UserData(
            nhs_number=NHS_NUMBER_PP_LETTER,
            message_reference=str(uuid.uuid4()),
            communication_type="LETTER",
            supplier="PRECISIONPROCO",
            personalisation="Mesh - Mixed Suppliers",
            contact_detail={
                "address": {
                    "lines": [
                        "3 Street",
                        "Town",
                        "City"
                    ],
                    "postcode": "LS10 1EL"
                }
            }
        ),
    ]

    Generators.generate_mesh_csv(test_users, "helpers/mesh-cli/sample_data.csv")

    mesh_helper.send_message("helpers/mesh-cli/sample_data.csv")
    aws_client.trigger_lambda(f"comms-{get_env()}-api-mpl-meshpoll")

    request_id = mesh_helper.retrieve_request_id()
    UserData.set_request_items_from_request_id(aws_client, test_users, request_id)
    api_helper.poll_test_users_for_status(test_users, ["sending", "delivered"])

    nhs_app_journey.nhs_app_login_and_view_message(
        ods_name="THE NORTH MIDLANDS AND EAST PROGRAMME FOR IT (NMEPFIT)",
        personalisation=UserData.get_by_nhs_number(NHS_NUMBER_NHSAPP, test_users).personalisation)

    UserData.enrich_test_data(aws_client, test_users)

    verify_email_content(UserData.get_by_nhs_number(NHS_NUMBER_EMAIL, test_users))
    verify_sms_content(UserData.get_by_nhs_number(NHS_NUMBER_SMS, test_users))
    aws_client.verify_mba_letter(UserData.get_by_nhs_number(NHS_NUMBER_MBA_LETTER, test_users))
    aws_client.verify_synertec_letter(UserData.get_by_nhs_number(NHS_NUMBER_SYNERTEC_LETTER, test_users))
    aws_client.verify_precision_proco_letter(UserData.get_by_nhs_number(NHS_NUMBER_PP_LETTER, test_users))
