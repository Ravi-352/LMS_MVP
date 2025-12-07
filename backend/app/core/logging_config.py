import logging
from logging.handlers import TimedRotatingFileHandler
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "client.log")

logger = logging.getLogger("client_logger")
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=7)
formatter = logging.Formatter('{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}')
handler.setFormatter(formatter)

logger.addHandler(handler)
