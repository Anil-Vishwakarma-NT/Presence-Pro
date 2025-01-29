import os
import sys
import os
# Add the parent directory of 'src' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import glob
import shutil
import logging
from datetime import datetime
from config.config import PROCESSED_FILES_FOLDER, SUBFOLDERS_FOR_UPLOAD_FOLDERS, CONSOLIDATED_FILE_PATH
from utils.logging_setup import setup_logging

 
 

def load_into_processed_folder():
    try:
        # Step 5: Create a timestamped folder in 'Processed Files'
        timestamp_folder_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        timestamped_folder_path = os.path.join(PROCESSED_FILES_FOLDER, timestamp_folder_name)
        os.makedirs(timestamped_folder_path)
        logging.info(f"Created timestamped folder: {timestamped_folder_path}")

        for folder_name, folder_path in SUBFOLDERS_FOR_UPLOAD_FOLDERS.items():
            logging.info(f"Processing folder: {folder_name}")
            # Since we've verified there's exactly one file, retrieve it
            excel_file = glob.glob(os.path.join(folder_path, '*.xlsx')) + glob.glob(os.path.join(folder_path, '*.xls'))
            if not excel_file:
                logging.warning(f"No Excel file found in folder: {folder_path}")
                continue

            # Move the file to the timestamped folder in 'Processed Files'
            destination_path = os.path.join(timestamped_folder_path, os.path.basename(excel_file[0]))
            shutil.move(excel_file[0], destination_path)
            logging.info(f"Moved file {excel_file[0]} to {destination_path}")

        logging.info(CONSOLIDATED_FILE_PATH)
        if os.path.exists(CONSOLIDATED_FILE_PATH):
            destination_consolidated_path = os.path.join(timestamped_folder_path, os.path.basename(CONSOLIDATED_FILE_PATH))
            shutil.move(CONSOLIDATED_FILE_PATH, destination_consolidated_path)
            logging.info(f"Moved consolidated file to {destination_consolidated_path}")
        else:
            logging.warning("Consolidated file 'consolidated_attendence_optimized.xlsx' not found in root folder.")

    except Exception as e:
        logging.exception("An error occurred while loading files into the processed folder.")
        raise