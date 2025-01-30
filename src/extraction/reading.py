# Read Files
import sys
import os
# Add the parent directory of 'src' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
 
import glob
import logging
from utils.common import create_folder, get_processing_excel_file_path
from config.config import *
from utils.logging_setup import setup_logging

# # # Initialize logging
# # setup_logging()

def extract_excel_file_path():
    try:
        # Step 1: Check and create 'Upload Here' and 'Processed Files' folders if they don't exist
        logging.info("Creating 'Upload Here','Processed Files' and 'email_detials' folders if they don't exist.")
        create_folder(UPLOAD_FOLDER)
        create_folder(PROCESSED_FILES_FOLDER)
        create_folder(EMAIL_DETAILS_FOLDER)

        # Step 2: Check and create subfolders within 'Upload Here'
        logging.info("Creating subfolders within 'Upload Here'.")
        for folder_name, folder_path in SUBFOLDERS_FOR_UPLOAD_FOLDERS.items():
            folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
            SUBFOLDERS_FOR_UPLOAD_FOLDERS[folder_name] = folder_path
            create_folder(folder_path)

        # Step 3: Verify each subfolder contains exactly one Excel file
        logging.info("Verifying each subfolder contains exactly one Excel file.")
        missing_or_extra_files = []

        for folder_name, folder_path in SUBFOLDERS_FOR_UPLOAD_FOLDERS.items():
            # Use glob to list Excel files in the current subfolder
            excel_files = glob.glob(os.path.join(folder_path, '*.xlsx')) + glob.glob(os.path.join(folder_path, '*.xls'))
            # Check if there is exactly one file; if not, add to missing_or_extra_files
            if len(excel_files) != 1:
                missing_or_extra_files.append(folder_name)

        # Step 4: Raise an exception if there is not exactly one Excel file in each required folder
        if missing_or_extra_files:
            logging.error(f"Each of the following folders must contain exactly one Excel file: {', '.join(missing_or_extra_files)}")
            raise Exception(f"Each of the following folders must contain exactly one Excel file: {', '.join(missing_or_extra_files)}")

        # Step 5: If exactly one file is found in each folder, read them into separate pandas dataframes
        logging.info("Reading Excel files into separate pandas dataframes.")
        excel_path_dict = get_processing_excel_file_path(SUBFOLDERS_FOR_UPLOAD_FOLDERS)

        logging.info("Excel file paths extracted successfully.")
        return excel_path_dict

    except Exception as e:
        logging.exception("An error occurred while extracting Excel file paths.")
        raise





 