from ultralytics import YOLO
import os
import random

def verify():
    # Load the custom trained model
    model_path = '/Users/andypandy/runs/detect/train2/weights/best.pt'
    if not os.path.exists(model_path):
        print("Model not found! Did training finish?")
        return

    model = YOLO(model_path)
    
    # Pick a random image from the validation set
    val_images_dir = 'data/dataset/images/val'
    files = [f for f in os.listdir(val_images_dir) if f.endswith('.jpg')]
    
    if not files:
        print("No validation images found.")
        return
        
    test_image_name = random.choice(files)
    test_image_path = os.path.join(val_images_dir, test_image_name)
    
    print(f"Testing model on: {test_image_name}")
    
    # Run Inference
    results = model(test_image_path)
    
    # Save result
    for r in results:
        r.save(filename=f"verification_result_{test_image_name}") # save to current dir
        
    print(f"Verification complete! Result saved as verification_result_{test_image_name}")
    print("Open this file to see the detection boxes.")

if __name__ == "__main__":
    verify()
