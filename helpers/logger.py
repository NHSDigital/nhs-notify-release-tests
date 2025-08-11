import logging

def get_logger(name: str = None) -> logging.Logger:
    return logging.getLogger(name)
    
def configure_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )