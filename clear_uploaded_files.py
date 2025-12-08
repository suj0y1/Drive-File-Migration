import csv
import os
from datetime import datetime
from utils_drive import authenticate
from googleapiclient.errors import HttpError

LOG_PATH = 'migration_log.csv'
CLEARED_COLUMN = 'ClearedTimestamp'
SIZE_COLUMN = 'FileSizeMB'

def ensure_log_columns():
    """Ensure the log file has the required headers."""
    with open(LOG_PATH, 'r', newline='') as csvfile:
        reader = list(csv.reader(csvfile))
        header = reader[0]
        changed = False

        if CLEARED_COLUMN not in header:
            header.append(CLEARED_COLUMN)
            changed = True
        if SIZE_COLUMN not in header:
            header.append(SIZE_COLUMN)
            changed = True

        if changed:
            with open(LOG_PATH, 'w', newline='') as out:
                writer = csv.writer(out)
                writer.writerow(header)
                writer.writerows(reader[1:])

def get_file_size_mb(service, file_id):
    try:
        meta = service.files().get(fileId=file_id, fields='size').execute()
        size = int(meta.get('size', 0))
        return round(size / (1024 * 1024), 2)
    except Exception:
        return 0.0

def delete_file(service, file_id):
    try:
        service.files().delete(fileId=file_id).execute()
        return True
    except HttpError as e:
        print(f"❌ Failed to delete {file_id}: {e}")
        return False

def clear_uploaded_files():
    ensure_log_columns()
    service = authenticate('account1_download')

    total_freed = 0.0
    with open(LOG_PATH, 'r', newline='') as csvfile:
        reader = list(csv.reader(csvfile))
        header = reader[0]
        rows = reader[1:]

    updated_rows = []
    for row in rows:
        # Pad the row to ensure it has enough columns
        while len(row) < len(header):
            row.append('')

        file_id = row[2].strip()
        uploaded = row[header.index('UploadTimestamp')].strip()
        cleared = row[header.index(CLEARED_COLUMN)].strip()

        if uploaded and not cleared:
            size_mb = get_file_size_mb(service, file_id)
            if delete_file(service, file_id):
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                row[header.index(CLEARED_COLUMN)] = timestamp
                row[header.index(SIZE_COLUMN)] = str(size_mb)
                total_freed += size_mb
                print(f"✅ Deleted {row[0]} ({size_mb} MB)")

        updated_rows.append(row)

    with open(LOG_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(updated_rows)

    print(f"\n🧹 Total space cleared: {round(total_freed, 2)} MB")

if __name__ == '__main__':
    clear_uploaded_files()

