from notifications_python_client.notifications import NotificationsAPIClient
import os

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