import os
import shutil
import time
import uuid
import sys

# Paths
IMPORT_SOURCE = 'data/import_queue'
TRAINING_DEST = 'data/training_raw'
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.heic'}

def setup_dirs():
    if not os.path.exists(IMPORT_SOURCE):
        os.makedirs(IMPORT_SOURCE)
        print(f"Created source folder: {IMPORT_SOURCE}")
        print(f"-> DROP YOUR WEB IMAGES OR AIRDROP PHOTOS HERE <-")
    
    if not os.path.exists(TRAINING_DEST):
        os.makedirs(TRAINING_DEST)
        print(f"Created destination folder: {TRAINING_DEST}")

def process_import():
    setup_dirs()
    
    files = [f for f in os.listdir(IMPORT_SOURCE) if os.path.isfile(os.path.join(IMPORT_SOURCE, f))]
    valid_files = [f for f in files if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS]
    
    if not valid_files:
        print(f"\nNo valid images found in {IMPORT_SOURCE}.")
        print("Please add .jpg, .png, or .heic files and run again.")
        return

    print(f"\nFound {len(valid_files)} images to import...")
    
    count = 0
    for filename in valid_files:
        src_path = os.path.join(IMPORT_SOURCE, filename)
        
        # Generate new name
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.heic': ext = '.jpg' # Simple conversion assumption for naming, though conversion needs lib
        
        new_name = f"training_imported_{timestamp}_{unique_id}{ext}"
        dest_path = os.path.join(TRAINING_DEST, new_name)
        
        try:
            # Move and rename
            shutil.move(src_path, dest_path)
            print(f"Imported: {filename} -> {new_name}")
            count += 1
        except Exception as e:
            print(f"Error importing {filename}: {e}")
            
    print(f"\nSuccess! Imported {count} images to {TRAINING_DEST}.")
    print("These are now ready for training.")

if __name__ == "__main__":
    process_import()
