import logging
import os
import sys


sys.path.append(os.path.abspath('..'))

def setup_logging(log_file):
    # Ensure logs directory exists
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    # Reset logging handlers if already configured
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s : %(message)s',
        handlers=[
            logging.FileHandler(log_file),  # Log to file
            logging.StreamHandler()  # Log to console
        ]
    )

# Define the base directory of the project
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
log_file = os.path.join(base_dir, "logs", "pipeline.log")
print(f"Log file path: {log_file}")
setup_logging(log_file)

# Test logging
logger = logging.getLogger(__name__)
logger.info("Logging setup complete. Test log message.")
