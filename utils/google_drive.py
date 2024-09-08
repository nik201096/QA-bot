import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

CREDS_FILE = "Your credentials"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_google_drive():
    creds = service_account.Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def extract_folder_id(shared_link):
    match = re.search(r'folders/([a-zA-Z0-9_-]+)', shared_link)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Drive folder link")

def is_file_link(shared_link):
    return 'drive.google.com' in shared_link and '/file/' in shared_link

def list_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, pageSize=1000, fields="files(id, name)").execute()
    items = results.get('files', [])
    return items

def download_file_from_google_drive(service, file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    return fh.getvalue()
