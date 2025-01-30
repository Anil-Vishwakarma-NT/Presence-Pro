import pandas as pd
import re
import logging
from openpyxl import load_workbook
from openpyxl.styles import Font
from src.notifications.email_notification import send_email
from config.notification_config import EmployeeEmailData
from config.config import CONSOLIDATED_FILE_PATH as consolidated_file_path
from utils.logging_setup import setup_logging


 
def validate_and_load_data(file_path, header_row = 0, skipfooter_row = 0, engine='openpyxl'):
    try:
        # Load the Excel file into a DataFrame
        return pd.read_excel(file_path, header=header_row, skipfooter=skipfooter_row, engine=engine)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File not found - {file_path}")
    except Exception as e:
        raise Exception(f"Error while reading file {file_path}: {e}")

def preprocess_employee_names(df, column_name):
    # Strip whitespace and convert names to uppercase for consistency
    if column_name in df.columns:
        df[column_name] = df[column_name].str.strip().str.upper()
    return df

def handle_duplicates(df, key_column):
    # Identify and separate duplicate records based on a specific column
    duplicates = df[df.duplicated(subset=[key_column], keep=False)]
    # Remove duplicate records from the original DataFrame
    df = df.drop_duplicates(subset=[key_column], keep=False)
    return df, duplicates

 

def transformation(keka_path, employee_email_data_path = EmployeeEmailData):
    try:
        # Load and preprocess employee email data
        email_info_df = validate_and_load_data(employee_email_data_path, header_row=2)
        preprocess_employee_names(email_info_df, 'Employee Name')
        email_info_df.set_index('Employee Number', inplace=True)
    except Exception as e:
        raise Exception(f"Error processing Employee Email data: {e}")

    try:
        # Load and preprocess Keka data
        keka_df = validate_and_load_data(keka_path, header_row=2,skipfooter_row=26)
        keka_df = preprocess_employee_names(keka_df, 'Employee Name')
    except Exception as e:
        raise Exception(f"Error processing Keka data: {e}")

    # try:
    #     # Preprocess and merge biometric data
    #     biometrics_df = preprocess_and_merge_biometric_data(indore_biometric_path, raipur_biometric_path)
    #     biometrics_df = preprocess_employee_names(biometrics_df, 'Employee Name')
    # except Exception as e:
    #     raise Exception(f"Error processing biometric data: {e}")

    # Handle duplicate records in Keka and Biometric data
    keka_df, keka_duplicates = handle_duplicates(keka_df, 'Employee Number')
    # biometrics_df, bio_duplicates = handle_duplicates(biometrics_df, 'Employee Name')

    # Set index for quick lookup
    keka_df.set_index('Employee Number', inplace=True)
    # biometrics_df.set_index('Employee Name', inplace=True)

    # Identify common employees between Keka and Biometric data
    # common_employees = keka_df.index.intersection(biometrics_df.index)
    # print(f"Number of common employees: {len(common_employees)}")
    
        # Indices in biometrics_df but not in keka_df
    # uncommon_indices = biometrics_df.index.difference(keka_df.index)
    # logging.info(f"Number of uncommon employees: {len(uncommon_indices)}")
    # Display the uncommon indices
    # logging.info(f"Name of uncommon employees: {uncommon_indices}")
    # if len(common_employees) == 0:
        # raise ValueError("No common employees found between Keka and Biometric data.")

    # Identify date columns in Keka data using regex
    date_pattern = re.compile(r'\d{2}-[a-zA-Z]{3}-\d{4}')
    date_columns = [col for col in keka_df.columns if date_pattern.match(col)]
    if not date_columns:
        raise ValueError("No date columns found in Keka DataFrame.")

    # Map Keka date columns to Biometric day numbers
    day_map = {col: str(int(col.split('-')[0])) for col in date_columns}
    # missing_days = set(day_map.values()) - set(biometrics_df.columns.astype(str))
    # for col, day in list(day_map.items()):
    #     if day in missing_days:
    #         logging.info(f"Removing date column '{col}' due to missing day '{day}' in Biometric data.")
    #         del day_map[col]

    # if not day_map:
    #     raise ValueError("No valid date mappings found between Keka and Biometric data.")

    for employee in keka_df.index:
        # bio_absent_count = 0
        # bio_present_count = 0
        employee_absent_dates = []
        CO = 0

        for keka_date, day in day_map.items():
            # Get attendance values for the current date
            keka_val = keka_df.at[employee, keka_date] if pd.notna(keka_df.at[employee, keka_date]) else None
            # biometric_val = biometrics_df.at[employee, day] if pd.notna(biometrics_df.at[employee, day]) else None

            # if biometric_val == 'P' and keka_val != 'WO':
            #     bio_present_count += 1

            # if biometric_val == 'A' and keka_val != 'WO':
            #     bio_absent_count += 1
                
            if keka_val == 'CO':
                CO += 1    

            # if keka_val == 'A' and biometric_val == 'P':
            #     # Update Keka data if biometric shows present but Keka shows absent
            #     keka_df.at[employee, keka_date] = 'P'
            #     keka_df.at[employee, 'Absent Days'] -= 1
            #     keka_df.at[employee, 'Present Days'] += 1

            if keka_val == 'A':
                # Record dates where both systems show absence
                employee_absent_dates.append(keka_date)

        if employee_absent_dates:
            # Send email notification for absent dates
            dates_of_absence = ", ".join(employee_absent_dates)
            if employee in email_info_df.index:
                employee_name = email_info_df.at[employee, 'Employee Name']
                employee_email = email_info_df.at[employee, 'Email']
                reporting_manager = keka_df.at[employee, 'Reporting Manager']
                manager_email = None

                if reporting_manager:
                    
                    reporting_manager = reporting_manager.strip().upper()

                    # Search for the manager's email using the Employee Name column
                    manager_row = email_info_df[email_info_df['Employee Name'].str.upper() == reporting_manager]

                    if not manager_row.empty:
                        manager_email = manager_row.iloc[0]['Email']  # Get the manager's email
                    
                print(employee_name)
                print(manager_email)
                send_email(
                    name=employee_name,
                    email=employee_email,
                    dates_of_absence=dates_of_absence,
                    manager_name=reporting_manager,
                    manager_email=manager_email
                )
                logging.info(f"Email sent to {employee_name} {employee}")
            else:
                logging.info(f"{employee} email address does not exist in Email information file")


        # Update workday calculations
        keka_df.at[employee, 'WOH'] = keka_df.at[employee, 'WOH']
        keka_df.at[employee, 'Comp Offs Taken'] = CO
        keka_df.at[employee, 'Available Comp Offs'] = keka_df.at[employee, 'WOH'] - CO
        # keka_df.at[employee, 'Biometric Absent Count'] = bio_absent_count - (
        #     keka_df.at[employee, 'Holidays'] +
        #     keka_df.at[employee, 'Total Paid Leave'] +
        #     keka_df.at[employee, 'Total Unpaid Leave']
        # )
        # keka_df.at[employee, 'Biometric Present Count'] = bio_present_count
        
        keka_df.at[employee, 'Total Work Days'] = keka_df.at[employee, 'Total Days'] - (
            keka_df.at[employee, 'Weekly Offs'] +
            keka_df.at[employee, 'Holidays'] +
            keka_df.at[employee, 'Total Paid Leave'] +
            keka_df.at[employee, 'Total Unpaid Leave'] +
            keka_df.at[employee, 'Absent Days'] - 
            keka_df.at[employee, 'WOH']
        )

    # Reset index for the final DataFrame
    keka_df.reset_index(inplace=True)
    try:
        # Define columns to keep for the filtered sheet
        columns_to_keep = ['Employee Name', 'Present Days', 'Absent Days', 'WFH', 'Total Paid Leave', 'Total Unpaid Leave', 'Holidays', 'Total Work Days', 'WOH', 'Comp Offs Taken', 'Available Comp Offs']
        filtered_df = keka_df[columns_to_keep]

        # Write data to an Excel file with multiple sheets
        with pd.ExcelWriter(consolidated_file_path, engine='openpyxl') as writer:
            keka_df.to_excel(writer, sheet_name='Keka_Sheet', index=False)
            filtered_df.to_excel(writer, sheet_name='FilteredColumns', index=False)
            keka_duplicates.to_excel(writer, sheet_name='Duplicate_Records', index=False, startrow=2)
            
        # Now load the workbook and append additional data
        wb = load_workbook(consolidated_file_path)
        ws = wb['Duplicate_Records']

        # Add header above Keka duplicates data
        ws["A1"] = "Duplicated Records for Keka"
        ws["A1"].font = Font(bold=True, size=14)

        # Add bio_duplicates data starting after keka_duplicates data
        start_row = keka_duplicates.shape[0] + 6
        ws[f"A{start_row}"] = "Duplicated Records for Biometric"
        ws[f"A{start_row}"].font = Font(bold=True, size=14)

        # # Write headers for bio_duplicates manually
        # for col_idx, col_name in enumerate(bio_duplicates.columns, start=1):
        #     ws.cell(row=start_row + 2, column=col_idx, value=col_name).font = Font(bold=True)

        # # Write bio_duplicates data starting after the header row for Bio
        # for r_idx, row in enumerate(bio_duplicates.values, start=start_row + 3):
        #     for c_idx, value in enumerate(row, start=1):
        #         ws.cell(row=r_idx, column=c_idx, value=value)

        # Save the workbook
        wb.save(consolidated_file_path)
        print(f"Transformation complete. Saved to '{consolidated_file_path}'.")
        return consolidated_file_path
    except PermissionError:
        print(f"Permission denied: Could not save to '{consolidated_file_path}'. Ensure the file is closed before running the script.")
    except Exception as e:
        raise Exception(f"Error saving the transformed data: {e}")




def preprocess_and_merge_biometric_data(indore_path, raipur_path, indore_header=8, raipur_header=5):
    """
    This function preprocesses two Excel files for biometric attendance data (Indore and Raipur),
    standardizes them, and merges them into a single DataFrame.
    Parameters:
    indore_path (str): Path to the Indore biometric Excel file.
    raipur_path (str): Path to the Raipur biometric Excel file.
    indore_header (int): Header row index for the Indore file (default is 8).
    raipur_header (int): Header row index for the Raipur file (default is 5).
    Returns:
    pd.DataFrame: The merged DataFrame containing preprocessed data from both files.
    """
    try:
        # Load and preprocess employee email data
        # email_info_df = validate_and_load_data(raipur_path, header_row=raipur_header)
        # preprocess_employee_names(email_info_df, 'Employee Name')
        # Load the Indore file
        indore = validate_and_load_data(indore_path, header_row=indore_header)
        # Load the Raipur file
        raipur = validate_and_load_data(raipur_path, header_row=raipur_header)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {e.filename}")
    except Exception as e:
        raise ValueError(f"Error loading Indore file: {e}")
    try:
        # Preprocess Indore data
        indore.drop(columns=['Unnamed: 0', 'Unnamed: 1'], inplace=True, errors='ignore')  # Ignore missing columns
        indore.rename(columns={'Unnamed: 2': 'Employee Name'}, inplace=True)
        indore = indore.dropna(axis=1, how='all')  # Drop columns that are completely empty
        indore = indore[indore['Employee Name'].notna()]  # Remove rows where 'Employee Name' is NaN
        # Clean columns: Drop columns that do not match the date pattern
        for column in indore.columns:
            if column != 'Employee Name' and not re.match(r'\d', column):
                indore.drop(columns=column, inplace=True, errors='ignore')
        # Replace 'MIS' with 'P' and fill NaNs with 'A'
        indore.replace('MIS', 'P', inplace=True)
        indore.fillna('A', inplace=True)
    except Exception as e:
        raise ValueError(f"Error processing Indore file: {e}")  
    try:
        # Preprocess Raipur data
        raipur = raipur.dropna(how='all')  # Drop rows that are completely empty
        # raipur = raipur.dropna(axis=1, how='all')  # Drop columns that are completely empty
        raipur.drop(columns=['Employee ID', 'Department'], inplace=True, errors='ignore')  # Ignore missing columns
        # Clean columns: Drop columns that do not match the date pattern
        for column in raipur.columns:
            if column != 'First Name' and not re.match(r'\d', column):
                raipur.drop(columns=column, inplace=True, errors='ignore')
    except Exception as e:
        raise ValueError(f"Error processing Raipur file: {e}")
    # Check for column mismatch
    if len(indore.columns) != len(raipur.columns):
        raise ValueError(f"Mismatch in the number of columns between Indore and Raipur files. "
                         f"Indore has {len(indore.columns)} columns, Raipur has {len(raipur.columns)} columns.")
    try:
        # Standardize the column names to match the Indore DataFrame
        # raipur.rename(columns={'First Name': 'Employee Name'}, inplace=True)
        raipur.columns = indore.columns
    except Exception as e :
        raise ValueError(f"Mismatch the number of columns in indore and raipur files")
    try:
        # Merge the two DataFrames
        union_df = pd.concat([indore, raipur], ignore_index=True)
    except Exception as e:
        raise ValueError(f"Error merging dataframes: {e}")
    return union_df
