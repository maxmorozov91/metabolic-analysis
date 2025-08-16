import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

logs_dir = Path(os.getcwd()) / "logs"
os.makedirs(logs_dir, exist_ok=True)
file_handler = logging.FileHandler(logs_dir / "main.log")
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)