import logging
import os

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"{log_dir}/app.log"),
            logging.StreamHandler()
        ]
    )

    # Return a logger instance to use globally
    return logging.getLogger()
