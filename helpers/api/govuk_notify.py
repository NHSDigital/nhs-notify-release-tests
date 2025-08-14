from notifications_python_client.notifications import NotificationsAPIClient
import os
import time
from helpers.logger import get_logger

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

def get_pdf(gukn_id):
    notifications_client = NotificationsAPIClient(os.environ["GUKN_API_KEY"])
    pdf = notifications_client.get_pdf_for_letter(gukn_id)
    with open("tests/evidence/gukn_letter.pdf", "wb") as f:
        f.write(pdf.getbuffer())

def verify_sms_content(user):
    # Query GUKN for record
    gukn_response = get_message(user.gukn_id)
    gukn_record = gukn_response['notifications'][0]
    assert user.personalisation in gukn_record['body']
    assert gukn_record['phone_number'] == user.contact_detail
    logger.info(f"SMS Appears as expected for user {user.nhs_number}")

def verify_email_content(user):
    gukn_response = get_message(user.gukn_id)
    gukn_record = gukn_response['notifications'][0]
    assert user.personalisation in gukn_record['body']
    assert gukn_record['email_address'] == user.contact_detail
    logger.info(f"Email Appears as expected for user {user.nhs_number}")
    
def verify_gukn_letter(user):
    end_time = time.time() + 60
    while time.time() < end_time:
        try:
            gukn_response = get_message(user.gukn_id)
            id = gukn_response['notifications'][0]['id']
            break
        except:
            logger.info(f"Waiting for GUKN letter for user {user.nhs_number} to be available")
            time.sleep(5)
    get_pdf(id)
    assert os.path.exists('tests/evidence/gukn_letter.pdf')
    logger.info(f"Letter PDF exists for user {user.nhs_number}")
