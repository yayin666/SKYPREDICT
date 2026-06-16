import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logger
logger = logging.getLogger("SkyPredict")
logger.setLevel(logging.INFO)

# File handler
fh = logging.FileHandler("logs/skypredict.log")
fh.setLevel(logging.INFO)

# Console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.ERROR) # Only print errors to console to keep Streamlit clean

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

def log_event(event_type: str, message: str):
    logger.info(f"[{event_type.upper()}] {message}")

def log_error(error_msg: str):
    logger.error(error_msg)
