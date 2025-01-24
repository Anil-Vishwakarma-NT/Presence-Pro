import logging

def setup_logging(log_level=logging.INFO, log_format='%(asctime)s - %(levelname)s - %(message)s', log_file=None):
    # Set the basic configuration for logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        filename=log_file,  # If None, logs are sent to the console
        filemode='a'  # Append mode if logging to a file
    )

    # If log_file is None, add a StreamHandler to output logs to the console
    if log_file is None:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(console_handler)