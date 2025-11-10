from install_playwright import install
from playwright.sync_api import expect, sync_playwright
import re
import os
from helpers.logger import get_logger
from helpers.constants import PATH_TO_EVIDENCE

def nhs_app_login_and_view_message(ods_name="NHS ENGLAND - X26", personalisation=None):
    logger = get_logger(__name__)

    with sync_playwright() as playwright:
        install(playwright.chromium)
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.set_default_timeout(30000)
        expect.set_options(timeout=30000)

        page.goto("https://www-onboardingaos.nhsapp.service.nhs.uk/login")
        logger.info("Accessed NHS App Onboarding AOS")

        expect(page.get_by_role("heading", name="Use NHS App services", exact=True)).to_be_visible()
        page.get_by_role("button", name="Continue").click()
        logger.info("Continuing on to username page")

        expect(page.get_by_role("heading", name="Log in to NHS App")).to_be_visible()
        page.get_by_role("textbox", name="Email address", exact=True).fill(os.environ['NHS_APP_USERNAME'])
        page.get_by_role("textbox", name="Password", exact=True).fill(os.environ['NHS_APP_PASSWORD'])
        page.get_by_role("button", name="Continue").click()
        logger.info("Entered username and password")

        expect(page.get_by_role("heading", name="Enter the security code")).to_be_visible()
        page.get_by_label("Security code", exact=True).fill(os.environ['NHS_APP_OTP'])
        page.get_by_role("button", name="Continue").click()
        logger.info("Entered OTP")

        page.wait_for_url('**/patient/')
        expect(page.get_by_text('NHS number: 972 854 4030')).to_be_visible()
        logger.info("Login journey success!")

        link_text = re.compile(r"You have \d+ unread messages")
        page.get_by_role("link", name=link_text).click()
        logger.info("Navigated to messages")

        expect(page.get_by_role("heading", name="Your messages")).to_be_visible()
        page.get_by_role("link", name="Unread message from", exact=False).first.click()
        logger.info("Selected unread messages")

        page.wait_for_url("**/patient/messages/app-messaging/app-message?messageId=**")
        expect(page.get_by_role("heading", name=ods_name)).to_be_visible()
        expect(page.get_by_text(f"NHS Notify Release: {personalisation}")).to_be_visible()
        evidence_path = f"{PATH_TO_EVIDENCE}/{personalisation.replace(' ', '_')}/nhsapp.png"
        page.screenshot(path=evidence_path)
        logger.info("NHS App message appears as expected")

        page.get_by_role("link", name="Home", exact=True).click()
        page.get_by_role("link", name="Log out").click()