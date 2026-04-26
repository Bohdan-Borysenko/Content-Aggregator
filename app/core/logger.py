import logging
import sys
from pathlib import Path

# Path to the log folder
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def setup_logging():
    logger = logging.getLogger("insight_flow")
    logger.setLevel(logging.INFO)

    # Post format: Date - Name - Level - Message
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 1. Output to the console (Docker logs)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. Вывод ошибок в файл
    file_handler = logging.FileHandler(LOG_DIR / "errors.log")
    file_handler.setLevel(logging.ERROR) 
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logging()