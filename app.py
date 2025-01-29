from src.extraction.reading import extract_excel_file_path
from src.transform.new_transformation import transformation
from src.load.load import load_into_processed_folder
from utils.logging_setup import setup_logging 

def obtimize_attendance_data():
    excel_file_path_dict = extract_excel_file_path()
    

    keka_excel_path = excel_file_path_dict["One Keka Excel File"]
    indore_bio_excel_path = excel_file_path_dict["One Indore Biometric Excel File"]
    raipur_bio_excel_path = excel_file_path_dict["One Raipur Biometric Excel File"]

    transformation(keka_excel_path,indore_bio_excel_path,raipur_bio_excel_path)

    load_into_processed_folder()


excel_file_path_dict = extract_excel_file_path()
    

keka_excel_path = excel_file_path_dict["One Keka Excel File"]
indore_bio_excel_path = excel_file_path_dict["One Indore Biometric Excel File"]
raipur_bio_excel_path = excel_file_path_dict["One Raipur Biometric Excel File"]

transformation(keka_excel_path,indore_bio_excel_path,raipur_bio_excel_path)

load_into_processed_folder()
