import pandas as pd
import re
from openpyxl import load_workbook
from openpyxl.styles import Font
from config.config import CONSOLIDATED_FILE_PATH
from src.notifications.email_notification import send_email
from config.notification_config import EmployeeEmailData


 

def transformation(keka_path, indore_biometric_path, raipur_biometric_path, employee_email_data_path=EmployeeEmailData):
    try:
        # Load the Excel file into a Pandas DataFrame
        email_info_df = pd.read_excel(employee_email_data_path, header=2, engine='openpyxl')
        email_info_df['Employee Name'] = email_info_df['Employee Name'].str.strip().str.upper()
        email_info_df.set_index("Employee Name", inplace=True)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Error: Employee email file not found - {e}")
    except Exception as e:
        raise Exception(f"Error while reading Employee Email file: {e}")

    try:
        # Load the Excel file into a Pandas DataFrame
        keka_df = pd.read_excel(keka_path, header=2, skipfooter=26, engine='openpyxl')
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Error: Keka file not found - {e}")
    except Exception as e:
        raise Exception(f"Error while reading Keka file: {e}")

    try:
        # Get merged biometric dataframe with Indore and Raipur records
        biometrics_df = preprocess_and_merge_biometric_data(indore_biometric_path, raipur_biometric_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Error: Biometric file not found - {e}")
    except ValueError as e:
        raise ValueError(f"Error while merging biometric data: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error during biometric data processing: {e}")

    # Normalize employee names in both DataFrames to remove leading/trailing spaces and make them uppercase
    keka_df['Employee Name'] = keka_df['Employee Name'].str.strip().str.upper()
    biometrics_df['Employee Name'] = biometrics_df['Employee Name'].str.strip().str.upper()

    # Identify duplicates and separate them from each DataFrame
    keka_duplicates = keka_df[keka_df.duplicated(subset=['Employee Name'], keep=False)]
    bio_duplicates = biometrics_df[biometrics_df.duplicated(subset=['Employee Name'], keep=False)]

    # Remove all duplicates based on 'Employee Name' in both DataFrames
    keka_df = keka_df.drop_duplicates(subset=['Employee Name'], keep=False)
    biometrics_df = biometrics_df.drop_duplicates(subset=['Employee Name'], keep=False)

    # Set 'Employee Name' as index for fast lookup in both DataFrames
    keka_df.set_index('Employee Name', inplace=True)
    biometrics_df.set_index('Employee Name', inplace=True)

    # Ensure there are common employees to process
    common_employees = keka_df.index.intersection(biometrics_df.index)
    print(f"Number of common employees: {len(common_employees)}")
    if len(common_employees) == 0:
        raise ValueError("No common employees found between Keka and Biometric data.")

    # Identify date columns in Keka DataFrame
    date_pattern = re.compile(r'\d{2}-[a-zA-Z]{3}-\d{4}')
    date_columns = [col for col in keka_df.columns if date_pattern.match(col)]
    if not date_columns:
        raise ValueError("No date columns found in Keka DataFrame.")

    # Create a mapping from Keka date columns to Biometric day numbers
    day_map = {col: str(int(col.split('-')[0])) for col in date_columns}
    missing_days = set(day_map.values()) - set(biometrics_df.columns.astype(str))
    if missing_days:
        print(f"The following day columns are missing in Biometric DataFrame: {missing_days}")
        for col, day in list(day_map.items()):
            if day in missing_days:
                print(f"Removing date column '{col}' due to missing day '{day}' in Biometric data.")
                del day_map[col]
    if not day_map:
        raise ValueError("No valid date mappings found between Keka and Biometric data.")

    # Update attendance based on biometric data
    for employee in common_employees:
        bio_absent_count = 0
        bio_present_count = 0
        employee_absent_dates = []
        CO = 0
        for keka_date, day in day_map.items():
            keka_val = keka_df.at[employee, keka_date] if pd.notna(keka_df.at[employee, keka_date]) else None
            biometric_val = biometrics_df.at[employee, day] if pd.notna(biometrics_df.at[employee, day]) else None
            if biometric_val == 'P' and keka_val != 'WO':
                bio_present_count += 1
            if biometric_val == 'A' and keka_val != 'WO':
                bio_absent_count += 1
            if biometric_val == 'CO':
                CO += 1
            if keka_val == 'A' and biometric_val == 'P':
                keka_df.at[employee, keka_date] = 'P'
                keka_df.at[employee, 'Absent Days'] -= 1
                keka_df.at[employee, 'Present Days'] += 1
            if keka_val == 'A' and biometric_val == 'A':
                employee_absent_dates.append(keka_date)

        if employee_absent_dates:
            dates_of_absence = ", ".join(employee_absent_dates)
            if employee in email_info_df.index:
                employee_email_address = email_info_df.at[employee, "Email"]
                reporting_manager = keka_df.at[employee, "Reporting Manager"]
                reporting_manager_email_address = None
                if reporting_manager:
                    reporting_manager = reporting_manager.strip().upper()
                    if reporting_manager in email_info_df.index:
                        reporting_manager_email_address = email_info_df.at[reporting_manager, "Email"]
                send_email(
                    name=employee,
                    email=employee_email_address,
                    dates_of_absence=dates_of_absence,
                    manager_name=reporting_manager,
                    manager_email=reporting_manager_email_address,
                )
                print(f"Email sent to {employee}")
            else:
                print(f"{employee} email address does not exist in Email information file")

        # Add a 'Total Work Days' column
        keka_df.at[employee, 'Biometric Absent Count'] = bio_absent_count - (
            keka_df.at[employee, 'Holidays'] +
            keka_df.at[employee, 'Total Paid Leave'] +
            keka_df.at[employee, 'Total Unpaid Leave']
        )
        keka_df.at[employee, 'Biometric Present Count'] = bio_present_count
        
        keka_df.at[employee, 'WOH'] = keka_df.at[employee, 'WOH']
        keka_df.at[employee, 'Available Comp Offs'] = keka_df.at[employee, 'WOH'] - CO
        keka_df.at[employee, 'Comp Offs Taken'] = CO
                
        keka_df.at[employee, 'Total Work Days'] = keka_df.at[employee, 'Total Days'] - (
            keka_df.at[employee, 'Weekly Offs'] +
            keka_df.at[employee, 'Holidays'] +
            keka_df.at[employee, 'Total Paid Leave'] +
            keka_df.at[employee, 'Total Unpaid Leave'] +
            keka_df.at[employee, 'Absent Days'] - 
            keka_df.at[employee, 'WOH']
        )


    # Reset index
    keka_df.reset_index(inplace=True)
    try:
        # Select specific columns to keep in the new sheet
        columns_to_keep = ['Employee Name', 'Present Days', 'Absent Days', 'WFH', 'Total Paid Leave', 'Total Unpaid Leave', 'Holidays', 'Total Work Days', 'WOH', 'Comp Offs Taken', 'Available Comp Offs', 'Biometric Absent Count', 'Biometric Present Count']
        filtered_df = keka_df[columns_to_keep]

        # Write both the original DataFrame and the filtered DataFrame to a new Excel file with multiple sheets
        with pd.ExcelWriter(CONSOLIDATED_FILE_PATH, engine='openpyxl') as writer:
            keka_df.to_excel(writer, sheet_name='Keka_Sheet', index=False)
            filtered_df.to_excel(writer, sheet_name='FilteredColumns', index=False)
            keka_duplicates.to_excel(writer, sheet_name='Duplicate_Records', index=False, startrow=2)

        # Now load the workbook and append additional data
        wb = load_workbook(CONSOLIDATED_FILE_PATH)
        ws = wb['Duplicate_Records']

        # Add header above Keka duplicates data
        ws["A1"] = "Duplicated Records for Keka"
        ws["A1"].font = Font(bold=True, size=14)

        # Add bio_duplicates data starting after keka_duplicates data
        start_row = keka_duplicates.shape[0] + 6
        ws[f"A{start_row}"] = "Duplicated Records for Biometric"
        ws[f"A{start_row}"].font = Font(bold=True, size=14)

        # Write headers for bio_duplicates manually
        for col_idx, col_name in enumerate(bio_duplicates.columns, start=1):
            ws.cell(row=start_row + 2, column=col_idx, value=col_name).font = Font(bold=True)

        # Write bio_duplicates data starting after the header row for Bio
        for r_idx, row in enumerate(bio_duplicates.values, start=start_row + 3):
            for c_idx, value in enumerate(row, start=1):
                ws.cell(row=r_idx, column=c_idx, value=value)

        # Save the workbook
        wb.save(CONSOLIDATED_FILE_PATH)

        print(f"Transformation complete. Saved to '{CONSOLIDATED_FILE_PATH}'.")
        return CONSOLIDATED_FILE_PATH
    except PermissionError:
        print(f"Permission denied: Could not save to '{CONSOLIDATED_FILE_PATH}'. Ensure the file is closed before running the script.")
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
        # Load the Indore file
        indore = pd.read_excel(indore_path, header=indore_header)
        # Load the Raipur file
        raipur = pd.read_excel(raipur_path, header=raipur_header)
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

