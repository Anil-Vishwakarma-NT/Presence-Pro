import os
import glob
 



def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Created folder: {folder_name}")
    else:
        pass    

    
PROCESSING_EXCEL_PATH = {}
# Function to check exactly one Excel file and return its path
def get_processing_excel_file_path(SUBFOLDERS_FOR_UPLOAD_FOLDERS):
    for folder_name, folder_path in SUBFOLDERS_FOR_UPLOAD_FOLDERS.items():
        excel_files = glob.glob(os.path.join(folder_path, '*.xlsx')) + glob.glob(os.path.join(folder_path, '*.xls'))
        if len(excel_files) == 1:
            PROCESSING_EXCEL_PATH[folder_name] =  excel_files[0]  # Return the path if exactly one file is found
        else:
            raise Exception(f"Folder '{folder_path}' must contain exactly one Excel file.")    
    
    return PROCESSING_EXCEL_PATH     
    