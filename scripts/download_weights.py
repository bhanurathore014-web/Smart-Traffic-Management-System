import os
from pathlib import Path
from ultralytics import YOLO

def download_weights():
    """
    Downloads the YOLOv8 nano model weights.
    By loading the model via ultralytics, it automatically downloads 
    the .pt file to the current working directory if not found.
    We then move it to the models/weights/ directory.
    """
    weights_dir = Path("models/weights")
    weights_dir.mkdir(parents=True, exist_ok=True)
    
    model_name = "yolov8n.pt"
    target_path = weights_dir / model_name
    
    if target_path.exists():
        print(f"Weights already exist at: {target_path}")
        return
        
    print(f"Downloading {model_name}...")
    # This automatically downloads to the current directory
    model = YOLO(model_name)
    
    # Move it to models/weights/
    if Path(model_name).exists():
        os.rename(model_name, target_path)
        print(f"Successfully moved weights to {target_path}")
    else:
        print("Failed to locate downloaded weights file.")

if __name__ == "__main__":
    download_weights()
