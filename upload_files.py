import os
from utils_drive import authenticate, upload_file
import csv
from datetime import datetime

# 📁 ID of the shared 'Files' folder as seen by account2
SHARED_FOLDER_ID = 'PASTE_YOUR_FOLDER_ID_HERE'

# 🗂 Root path of the locally downloaded files
LOCAL_ROOT = 'downloaded_files/Files'

# 🔁 Build a mapping of relative path → folder ID for all subfolders in Files
def build_folder_map(service, parent_id, current_path=''):
    folder_map = {}
    query = f"'{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()

    for f in results.get('files', []):
        folder_name = f['name']
        folder_id = f['id']
        rel_path = os.path.join(current_path, folder_name)
        folder_map[rel_path] = folder_id
        # 🔁 Recurse into subfolders
        subfolders = build_folder_map(service, folder_id, rel_path)
        folder_map.update(subfolders)

    return folder_map

def mark_uploaded_by_id(file_id, log_path='migration_log.csv'):
    if not file_id:
        print(f"⚠️ No file ID provided. Cannot update log.")
        return

    rows = []
    updated = False

    with open(log_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 3 and row[2].strip() == file_id:
                # Ensure UploadTimestamp column (6th column)
                while len(row) < 6:
                    row.append('')
                row[5] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updated = True
            rows.append(row)

    if updated:
        with open(log_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)
    else:
        print(f"⚠️ Could not find matching file ID in log: {file_id}")

def upload_downloaded_files():
    service = authenticate('account2_upload')

    print("📥 Building folder map from shared Files folder...")
    folder_map = build_folder_map(service, SHARED_FOLDER_ID)
    print(f"✅ Found {len(folder_map)} folders in shared Files.")

    for root, dirs, files in os.walk(LOCAL_ROOT):
        rel_path = os.path.relpath(root, LOCAL_ROOT)
        rel_path = rel_path if rel_path != '.' else ''

        # Get matching folder ID in shared Files structure
        target_folder_id = folder_map.get(rel_path)
        if not target_folder_id:
            print(f"⚠️ Skipping folder (not found in shared Files): {rel_path}")
            continue

        for fname in files:
            local_path = os.path.join(root, fname)

            # 🔍 Find file ID and UploadTimestamp
            file_id = None
            already_uploaded = False
            with open('migration_log.csv', 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) >= 3 and row[0].strip() == fname.strip():
                        file_id = row[2].strip()
                        if len(row) >= 6 and row[5].strip() != '':
                            already_uploaded = True
                        break

            if already_uploaded:
                print(f"✅ Already uploaded: {fname} — Skipping")
                continue

            print(f"⬆️ Uploading {local_path} → Files/{rel_path or ''}")
            upload_file(service, local_path, target_folder_id)

            print(f"🔍 Marking upload in log by ID: {file_id}")
            mark_uploaded_by_id(file_id)



if __name__ == '__main__':
    upload_downloaded_files()

