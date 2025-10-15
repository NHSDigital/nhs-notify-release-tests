import re
import time
from helpers.bash import bash_command
from helpers.logger import get_logger
logger = get_logger(__name__)

class MeshHelper:
    def __init__(self, mailbox_name="NHS Notify UAT"):
        self.mailbox_name = mailbox_name
        self.logger = get_logger(__name__)

    def setup_cli(self):
        self.logger.info("Setting up MESH CLI...")
        bash_command("scripts/get_mesh_cli.sh")

    def send_message(self, csv_path, workflow_id="SEND_COMMS_TEST"):
        self.logger.info(f"Sending MESH message using CSV: {csv_path}")
        bash_command(
            f"mesh_send '{self.mailbox_name}' '{self.mailbox_name}' "
            f"1962c467-0000-0000-0000-3fa5cee00391 {csv_path} {workflow_id}"
        )

    def retrieve_request_id(self, max_retries=10, delay=5):
        self.logger.info("Retrieving MESH message...")
        output = bash_command(f"mesh_retrieve '{self.mailbox_name}' -p")

        for attempt in range(max_retries):
            if "No messages available." not in output:
                break
            self.logger.info(f"No messages yet (attempt {attempt+1}/{max_retries}), retrying...")
            time.sleep(delay)
            output = bash_command(f"mesh_retrieve '{self.mailbox_name}' -p")

        match = re.search(r'"requestId":"([^"]+)"', output)
        if not match:
            raise ValueError(f"Could not extract requestId from MESH retrieve output: {output}")

        request_id = match.group(1)
        self.logger.info(f"Retrieved MESH requestId: {request_id}")
        return request_id

