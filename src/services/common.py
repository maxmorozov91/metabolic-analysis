import logging
import os
import time
from datetime import timedelta
from functools import wraps
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logs_dir = Path(os.getcwd()) / "logs"
os.makedirs(logs_dir, exist_ok=True)
file_handler = logging.FileHandler(logs_dir / "main.log")
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        formatted_time = str(timedelta(seconds=duration))

        msg = ""

        if args:
            main_arg = args[0]
            msg = f"for {main_arg} "

        logger.info(f"'{func.__name__}' {msg}execution time: {formatted_time}")
        
        return result

    return wrapper
