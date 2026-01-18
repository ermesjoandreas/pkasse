from ultralytics import YOLO
import os

def train():
    # Load a model
    model = YOLO('yolov8n.pt')  # load a pretrained model (nano version)

    # Train the model
    # data argument points to the yaml file created by prepare script
    yaml_path = os.path.abspath('data/dataset/data.yaml')
    
    print(f"Starting training with config: {yaml_path}")
    
    results = model.train(
        data=yaml_path,
        epochs=50,       # Quick run
        imgsz=640,       # Standard image size
        plots=True,      # Save plots
        device='mps'     # Use Apple Silicon GPU if available, else 'cpu'
        # device='cpu'   # Force CPU if MPS has issues
    )
    
    print("Training Complete!")
    print(f"Best model saved at: {results.save_dir}/weights/best.pt")

if __name__ == "__main__":
    train()
