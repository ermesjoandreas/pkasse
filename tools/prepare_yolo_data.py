import os
import shutil
import random
import yaml

# Paths
RAW_DIR = 'data/training_raw'
DATASET_DIR = 'data/dataset'
IMAGES_DIR = os.path.join(DATASET_DIR, 'images')
LABELS_DIR = os.path.join(DATASET_DIR, 'labels')

def setup_directories():
    # Clean recreate
    if os.path.exists(DATASET_DIR):
        shutil.rmtree(DATASET_DIR)
    
    for split in ['train', 'val']:
        os.makedirs(os.path.join(IMAGES_DIR, split), exist_ok=True)
        os.makedirs(os.path.join(LABELS_DIR, split), exist_ok=True)

def create_yaml_config(classes):
    data_yaml = {
        'path': os.path.abspath(DATASET_DIR),
        'train': 'images/train',
        'val': 'images/val',
        'nc': len(classes),
        'names': classes
    }
    
    with open(os.path.join(DATASET_DIR, 'data.yaml'), 'w') as f:
        yaml.dump(data_yaml, f, default_flow_style=False)
    
    print(f"Created data.yaml with classes: {classes}")

def prepare_data():
    setup_directories()
    
    # Gather paired files (image + txt)
    files = [f for f in os.listdir(RAW_DIR) if f.endswith('.jpg') or f.endswith('.png')]
    paired_files = []
    
    # Read classes.txt if exists
    classes = ['postkasse'] # Default if file missing
    classes_file = os.path.join(RAW_DIR, 'classes.txt')
    if os.path.exists(classes_file):
        with open(classes_file, 'r') as f:
            classes = [line.strip() for line in f.readlines() if line.strip()]
            
    for img_file in files:
        basename = os.path.splitext(img_file)[0]
        txt_file = basename + '.txt'
        
        if os.path.exists(os.path.join(RAW_DIR, txt_file)):
            paired_files.append((img_file, txt_file))
            
    # Shuffle and Split
    random.shuffle(paired_files)
    split_idx = int(len(paired_files) * 0.8) # 80% train
    
    train_set = paired_files[:split_idx]
    val_set = paired_files[split_idx:]
    
    print(f"Total pairs: {len(paired_files)}")
    print(f"Training: {len(train_set)}")
    print(f"Validation: {len(val_set)}")
    
    def copy_set(dataset, split_name):
        for img, txt in dataset:
            shutil.copy(os.path.join(RAW_DIR, img), os.path.join(IMAGES_DIR, split_name, img))
            shutil.copy(os.path.join(RAW_DIR, txt), os.path.join(LABELS_DIR, split_name, txt))
            
    copy_set(train_set, 'train')
    copy_set(val_set, 'val')
    
    create_yaml_config(classes)
    print("\nDataset preparation complete! Ready for YOLO.")

if __name__ == "__main__":
    prepare_data()
