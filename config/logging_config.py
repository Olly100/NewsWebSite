import logging
import os

def setup_logging():
    # Ensure the logs directory exists
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Full path to the log file
    log_file_path = os.path.join(log_dir, "app.log")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,  # Set to DEBUG to capture all logs
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",  # Custom log format
        handlers=[
            logging.FileHandler(log_file_path),  # Log to the logs/app.log file
            logging.StreamHandler()  # Log to the console
        ]
    )

    # Return a logger with a specific name
    return logging.getLogger("MainPipeline")
