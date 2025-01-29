# import pandas as pd
# from googleapiclient.discovery import build
# from google.oauth2 import service_account
# from googleapiclient.http import MediaIoBaseDownload
# import io

# #/mnt/c/Users/DELL/Desktop/PRESENCE PRO 2.O/presencepro-cffe8fc610c7.json
# # Step 1: Set up service account credentials
# creds = service_account.Credentials.from_service_account_file(
#     '/presencepro-cffe8fc610c7.json',  # Path to your service account JSON file
#     scopes=['https://www.googleapis.com/auth/drive']
# )

# # Build the Drive API service
# drive_service = build('drive', 'v3', credentials=creds)

# # Step 2: Specify the file ID of the Excel file you want to read
# file_id = '<your_file_id_here>'  # Replace with the actual file ID from Google Drive

# # Step 3: Create a request to get the file metadata
# request = drive_service.files().get_media(fileId=file_id)

# # Step 4: Use BytesIO to read the file into memory instead of saving it locally
# file_stream = io.BytesIO()

# # Use MediaIoBaseDownload to download the file content to the in-memory stream
# downloader = MediaIoBaseDownload(file_stream, request)

# done = False
# while done is False:
#     status, done = downloader.next_chunk()
#     print(f"Download {int(status.progress() * 100)}%.")

# # Step 5: Use Pandas to read the Excel file from the in-memory stream
# file_stream.seek(0)  # Reset the stream position to the beginning
# df = pd.read_excel(file_stream)

# # Step 6: Display the DataFrame
# print(df.head())  # Display the first few rows of the DataFrame
