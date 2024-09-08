

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
TENANT_ID = "YOUR_TENANT_ID"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

import requests
import base64
import json
from msal import ConfidentialClientApplication

app = ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)

def get_access_token():
    result = app.acquire_token_silent(SCOPE, account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=SCOPE)
    return result['access_token']

def decode_shared_link(shared_link):
    encoded_link = base64.urlsafe_b64encode(shared_link.encode()).decode()
    return f"https://graph.microsoft.com/v1.0/shares/u!{encoded_link}/driveItem"

def download_files_from_onedrive(shared_link):
    try:
        access_token = get_access_token()
        headers = {'Authorization': 'Bearer ' + access_token}
        api_link = decode_shared_link(shared_link)
        response = requests.get(api_link, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch link info: {response.text}")
        
        data = response.json()
        file_list = []

        if 'folder' in data:
            # It's a folder, list the files in it
            folder_id = data['id']
            children_endpoint = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
            children_response = requests.get(children_endpoint, headers=headers)
            if children_response.status_code != 200:
                raise Exception(f"Failed to fetch folder contents: {children_response.text}")
            items = children_response.json().get('value', [])
            for item in items:
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
