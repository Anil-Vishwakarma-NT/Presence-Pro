from src.extraction.reading import extract_excel_file_path
from src.transform.new_transformation import transformation
from src.load.load import load_into_processed_folder



excel_file_path_dict = extract_excel_file_path()
 

keka_excel_path = excel_file_path_dict["One Keka Excel File"]
indore_bio_excel_path = excel_file_path_dict["One Indore Biometric Excel File"]
raipur_bio_excel_path = excel_file_path_dict["One Raipur Biometric Excel File"]

transformation(keka_excel_path,indore_bio_excel_path,raipur_bio_excel_path)

load_into_processed_folder()

# email_info_df = pd.read_excel(EmployeeEmailData, header=2, engine='openpyxl')
# email_info_df.set_index("Employee Name", inplace=True)
# print(email_info_df.at["Sakshi Purankar", "Email"])

#  name=employee,
#                         email=email_info_df.at[employee, "Email"],
#                         dates_of_absence=keka_date,
#                         manager_name=keka_df.at[employee, "Reporting Manager"],
#                         manager_email=email_info_df.at[keka_df.at[employee, "Reporting Manager"], "Email"]
                        
                                        
                    #             if keka_df.at[employee, "Reporting Manager"] in email_info_df.index:
                    #     reporting_manger = keka_df.at[employee, "Reporting Manager"]
                    # reporting_manger_email_address=None
                    # if reporting_manger in email_info_df.index:
                    #     reporting_manger_email_address = email_info_df.at[reporting_manger , "Email"]