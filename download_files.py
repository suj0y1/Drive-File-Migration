import os
from utils_drive import authenticate, download_file, get_full_path
import csv
from datetime import datetime

BOOKS_FOLDER_ID = 'PASTE_YOUR_FOLDER_ID_HERE' # Replace 'PASTE_YOUR_FOLDER_ID_HERE' with your actual folder ID that can be found from the url when you open the google drive folder in browser.
DOWNLOAD_ROOT = 'downloaded_files'
MAX_FILES_PER_BATCH = 10  # Adjust as needed


def list_owned_files_recursive(service, folder_id, path_prefix=''):
    files = []
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType, owners)"
    ).execute()

    for f in results.get('files', []):
        file_id = f['id']
        name = f['name']
        mimeType = f['mimeType']
        owner = f['owners'][0]['me']

        if mimeType == 'application/vnd.google-apps.folder':
            subfolder_files = list_owned_files_recursive(service, file_id, os.path.join(path_prefix, name))
            files.extend(subfolder_files)
        elif owner:
            files.append({
                'id': file_id,
                'name': name,
                'path': os.path.join(path_prefix, name)
            })

    return files

def ensure_log_exists(log_path='migration_log.csv'):
    if not os.path.exists(log_path):
        print(f"📝 Creating log file: {log_path}")
        with open(log_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "Filename", "RelativePath", "FileID",
                "Status", "Timestamp", "UploadTimestamp"
            ])


def append_to_log(file, rel_path, log_path='migration_log.csv'):
    with open(log_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            file['name'].strip(),
            rel_path.strip().replace('\\', '/'),
            file['id'].strip(),
            'Downloaded',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            ''  # Empty UploadTimestamp
        ])

def download_owned_files():
    service = authenticate('account1_download')

    # Step 1: Make sure log file exists
    log_path = 'migration_log.csv'
    if not os.path.exists(log_path):
        print(f"📝 Creating log file: {log_path}")
        with open(log_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "Filename", "RelativePath", "FileID",
                "Status", "Timestamp", "UploadTimestamp"
            ])

    # Step 2: Read existing logged file IDs to skip already downloaded
    logged_ids = set()
    with open(log_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # skip header
        for row in reader:
            if len(row) >= 3:
                logged_ids.add(row[2].strip())

    # Step 3: Get all owned files from the Books folder
    files = list_owned_files_recursive(service, BOOKS_FOLDER_ID)
    print(f"Found {len(files)} owned files in total.")

    # Step 4: Filter only new files
    to_download = [f for f in files if f['id'].strip() not in logged_ids]
    print(f"🆕 {len(to_download)} new files to download.")

    # Step 5: Limit to a batch size (e.g., 10)
    to_download = to_download[:50]

    for f in to_download:
        rel_path = f['path'].strip().replace('\\', '/')
        local_path = os.path.join('downloaded_books', 'Books', rel_path)

        # Make sure directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        print(f"📥 Downloading {f['name']} → {local_path}")
        download_file(service, f, local_path)

        # Step 6: Append this file to the migration log
        with open(log_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                f['name'].strip(),
                rel_path,
                f['id'].strip(),
                'Downloaded',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                ''  # Empty upload timestamp
            ])

    return len(to_download)  # Tell caller how many were downloaded


if __name__ == '__main__':
    download_owned_files()

