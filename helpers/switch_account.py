import subprocess
import os
from helpers.logger import get_logger

logger = get_logger(__name__)

def switch_aws_account():
    profile = os.getenv('AWS_PROFILE')
    if profile:
        subprocess.run(
            ["bash", "-c", f"setacc {profile}; echo $AWS_PROFILE"],
            capture_output=True, 
            text=True
        )
        logger.info(f"Switched to mgmt locally")
    else:
        subprocess.run(
            ["bash", "./helpers/scripts/switch_account.sh"], 
            capture_output=True, 
            text=True
        )
        logger.info(f"Switched to mgmt in CI/CD")