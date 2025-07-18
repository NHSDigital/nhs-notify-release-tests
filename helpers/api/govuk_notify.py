from notifications_python_client.notifications import NotificationsAPIClient
import os

def get_gukn_message():
    notifications_client = NotificationsAPIClient(os.environ["GUKN_API_KEY"])
    gov_uk_response = notifications_client.get_all_notifications("delivered").get("notifications")

    assert len(gov_uk_response) > 0

def get_message():
    notifications_client = NotificationsAPIClient(os.environ["GUKN_API_KEY"])
    gov_uk_response = notifications_client.get_all_notifications(
        'received',
        reference='301nxjRzqkthxsZHMh9hnOeiHKn_301o0G6nHfUV8e6QQ6M0l3hbVl5_2025-07-18_1'
    )
    return gov_uk_response