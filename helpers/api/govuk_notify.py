from notifications_python_client.notifications import NotificationsAPIClient
import os
from helpers.logger import get_logger
from helpers.evidence import save_evidence
logger = get_logger(__name__)

def get_gukn_message():
    notifications_client = NotificationsAPIClient(os.environ["GUKN_API_KEY"])
    gov_uk_response = notifications_client.get_all_notifications("delivered").get("notifications")

    assert len(gov_uk_response) > 0

def get_message(gukn_id):
    notifications_client = NotificationsAPIClient(os.environ["GUKN_API_KEY"])
    gov_uk_response = notifications_client.get_all_notifications(
        'received',
        reference=gukn_id
    )
    return gov_uk_response

def get_pdf(gukn_id, user):
    notifications_client = NotificationsAPIClient(os.environ["GUKN_API_KEY"])
    pdf = notifications_client.get_pdf_for_letter(gukn_id)
    evidence_path = f"{user.personalisation}/gukn_letter.pdf"
    save_evidence(pdf, evidence_location=evidence_path)

def verify_sms_content(user):
    # Query GUKN for record
    gukn_response = get_message(user.gukn_id)
    gukn_record = gukn_response['notifications'][0]
    assert user.personalisation in gukn_record['body']
    assert gukn_record['phone_number'] == user.contact_detail
    evidence_path=f"{user.personalisation}/gukn_sms.json"
    save_evidence(gukn_response, evidence_location=evidence_path)
    logger.info(f"SMS Appears as expected for user {user.nhs_number}")

def verify_email_content(user):
    gukn_response = get_message(user.gukn_id)
    gukn_record = gukn_response['notifications'][0]
    assert user.personalisation in gukn_record['body']
    assert gukn_record['email_address'] == user.contact_detail
    evidence_path=f"{user.personalisation}/gukn_email.json"
    save_evidence(gukn_response, evidence_location=evidence_path)
    logger.info(f"Email Appears as expected for user {user.nhs_number}")
