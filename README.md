# 📁 Google Drive File Migration Toolkit

This project helps you **migrate files** that you uploaded in a shared Google Drive folder (like "Files") from one Google account (`account1`) to another (`account2`), while maintaining the folder structure and tracking progress.

---

## 🚀 Why & When to Use  
- You’ve used a shared folder on one account and want to transfer your personal uploads to a new account.  
- You want a repeatable, logged, partially automated migration process with rollback/recovery support.  

---

## ✅ Features

- Downloads only the files **you own** from a shared folder.
- Uploads them from `account2` into the **same folder structure**.
- Tracks all progress in a `migration_log.csv`.
- Supports:
  - Resuming downloads/uploads
  - Re-downloading missed files
  - Skipping already uploaded files
  - Deleting files from `account1` after migration
  - Measuring space freed

---

## ✅ Requirements

- Python 3.7+
- Google Cloud Projects (one for each Google account)
- `credentials.json` files from both accounts

---

## 📁 Folder Structure

```md

drive_file_migration/
│
├── account1_download/             # For your first Google account (download)
│   ├── credentials.json           # OAuth2 credentials from account 1
│   └── token.json                 # Will be created after first login
│
├── account2_upload/              # For your second Google account (upload)
│   ├── credentials.json           # OAuth2 credentials from account 2
│   └── token.json                 # Will be created after first login
│
├── downloaded_books/
│   └── Books/                     # downloaded files appear here
│
├── migration_log.csv
│
├── utils_drive.py
├── download_files.py
├── upload_files.py
├── migrate_batch.py
├── clear_uploaded_files.py
└── README.md
└── .gitignore                     # Optional: ignore token files

```

---

## ⚙️ Setup Instructions

### 1. Enable Google Drive API and Get OAuth2 Credentials for each account

#### ✅ PART 1: Enable Google Drive API
- Go to [Google Cloud Console](https://console.cloud.google.com/):
  - Log in with the **Google account** you want to access.
  - Open: https://console.cloud.google.com/
- Create a project:
  - Click the project drop-down (top-left corner) → “**New Project**”
  - Give it a name (e.g., Drive File Migration)
  - Click Create.
- Select your new project (if not auto-selected):
  - Use the project selector in the top-left and choose your project.
- Enable the Google Drive API:
  - Go to this link (for the selected project): https://console.cloud.google.com/apis/library/drive.googleapis.com
  - Click Enable.

#### ✅ PART 2: Create OAuth2 Credentials
- Go to the Credentials Page:
  - https://console.cloud.google.com/apis/credentials
- Click “+ Create Credentials” → choose “OAuth 2.0 Client ID”
- Set up OAuth Consent Screen (if asked):
  - Choose External for User Type (it's fine even if only you use it)
  - Click Create
  - Enter:
    - App name (e.g., DriveTransferApp)
    - User support email: your email
    - Developer email address: your email
  - Click Save and Continue (you can skip scopes and test users for now).
- Choose Application Type:
  - Select Desktop app
  - Name it (e.g., Drive Transfer Tool)
  - Click Create
- Copy your credentials:
  - After creation, you’ll see:
    - Client ID
    - Client Secret
  - Click Download JSON
- Rename the downloaded file to credentials.json
- Put in:
  - For account 1: `drive_file_migration/account1_download/credentials.json`

#### Repeat for account 2
  - For account 2: `drive_file_migration/account2_upload/credentials.json`

### 2. First-Time Authentication

- Go to Google Cloud Console: https://console.cloud.google.com/apis/credentials
- Click “OAuth consent screen” in the left sidebar.
- Scroll to the “Test Users” section.
- Click “Add Users” → enter your Gmail address → click Save.
- Each script (download or upload) now will run a browser login the first time.


### 3. Install Dependencies

- $ pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

### 4. Step 1

edit download_files.py and upload_files.py and put the Google drive folder IDs of the shared folder

### 5. Step 2

python3 migrate_batch.py

### 6. Step 3

python3 clear_uploaded_files.py

### repeat few times 


🛡️ Notes

--- Never modify migration_log.csv manually unless necessary.

--- Only modify migration_log.csv if some files are downloaded but are not uploaded. In that case delete the entry from migration_log.csv and repeat from Step 2.

--- Always use consistent folder structure and names for paths to match properly.

--- You can adjust batch size in download_files.py for faster or slower migration.

--- Never commit credentials to public repos.


