import subprocess
from helpers.logger import get_logger


logger = get_logger(__name__)

def bash_command(command):
    """Execute a bash command and return its output."""
    try:
        output = subprocess.run(
            ["bash", "-c", command],
            capture_output=True,
            text=True
        )
        return output.stdout

    except subprocess.CalledProcessError as e:
        logger.error("❌ Command failed with exit code %d", e.returncode)
        logger.error("Output: %s", e.output)
