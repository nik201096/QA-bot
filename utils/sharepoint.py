import requests
import re
import io
from msal import ConfidentialClientApplication

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
TENANT_ID = "YOUR_TENANT_ID"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

app = ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)

def get_access_token():
    result = app.acquire_token_silent(SCOPE, account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=SCOPE)
    return result['access_token']

def download_files_from_sharepoint(shared_link):
    try:
        access_token = get_access_token()
        headers = {'Authorization': 'Bearer ' + access_token}
        response = requests.get(shared_link, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch link info: {response.text}")
        
        data = response.json()
        file_list = []
        
        if 'folder' in data:
            # It's a folder, list the files in it
            for item in data['folder']['value']:
                if item['name'].endswith(('.pdf', '.docx', '.txt', '.jpeg', '.png', '.jpg')):
                    file_response = requests.get(item['@microsoft.graph.downloadUrl'], headers=headers)
                    file_list.append((file_response.content, item['name']))
        else:
            # It's a file, download it
            file_response = requests.get(data['@microsoft.graph.downloadUrl'], headers=headers)
            file_list.append((file_response.content, data['name']))
        
        return file_list
    except Exception as e:
        print(f"Error: {e}")
        return []
