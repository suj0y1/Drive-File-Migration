import os
import shutil
import time
from download_files import download_owned_files
from upload_files import upload_downloaded_files

def clear_local_downloads(download_dir='downloaded_files'):
    if os.path.exists(download_dir):
        print(f"🧹 Cleaning up: removing {download_dir} ...")
        shutil.rmtree(download_dir)
    else:
        print("📂 No downloads found to clean.")

def main_loop():
    round_count = 1
    while True:
        print(f"\n🔄 ====== MIGRATION ROUND {round_count} ======\n")
        
        # Step 1: Download files owned by account1
        new_files_downloaded = download_owned_files()
        if new_files_downloaded == 0:
            print("✅ No new files to download. Migration complete!")
            break

        # Step 2: Upload files via account2
        upload_downloaded_files()

        # Step 3: Delete downloaded files to free space
        clear_local_downloads()

        round_count += 1
        time.sleep(2)  # Short pause for safety/log clarity

if __name__ == "__main__":
    main_loop()

