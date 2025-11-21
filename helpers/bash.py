import subprocess
from helpers.logger import get_logger


logger = get_logger(__name__)

def bash_command(command):
    """Execute a bash command and return its output."""
    try:
        output = subprocess.run(
            ["bash", "-c", command],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Executed command:\n{command}")
        return output.stdout.strip()

    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {command}")
        logger.error(f"Exit code: {e.returncode}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise