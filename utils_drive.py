import os
import io
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate(creds_path):
    creds = None
    token_path = os.path.join(creds_path, 'token.json')
    credentials_file = os.path.join(creds_path, 'credentials.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)
    
def get_file_metadata_by_id(service, file_id):
    return service.files().get(fileId=file_id, fields="id, name, mimeType, parents").execute()

def get_full_path(service, file_id, current_path=''):
    file = service.files().get(fileId=file_id, fields='id, name, parents').execute()
    name = file['name']
    parents = file.get('parents', [])
    if not parents:
        return os.path.join(name, current_path)
    else:
        return get_full_path(service, parents[0], os.path.join(name, current_path))

def download_file(service, file, local_path):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    request = service.files().get_media(fileId=file['id'])
    with open(local_path, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

def upload_file(service, local_path, parent_id):
    file_metadata = {
        'name': os.path.basename(local_path),
        'parents': [parent_id]
    }
    media = MediaFileUpload(local_path, resumable=True)
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return uploaded_file.get('id')

def create_folder(service, name, parent_id=None):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')
