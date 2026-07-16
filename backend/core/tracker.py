import numpy as np
from pathlib import Path
from ultralytics import YOLO
from typing import List, Dict, Any

class VehicleTracker:
    def __init__(self, model_path: str = "models/weights/yolov8n.pt", tracker_type: str = "bytetrack.yaml"):
        """
        Initializes the YOLOv8 vehicle tracker using ByteTrack.
        """
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model weights not found at {self.model_path}")
            
        self.model = YOLO(str(self.model_path))
        self.tracker_type = tracker_type
        
        # COCO mapping for traffic vehicles
        # 2: car, 3: motorcycle, 5: bus, 7: truck
        self.allowed_classes = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

    def track(self, frame: np.ndarray, conf_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Processes a BGR numpy array frame and returns bounding boxes 
        along with unique track IDs for detected traffic vehicles.
        """
        # persist=True is strictly required to keep object IDs across consecutive frames
        results = self.model.track(
            frame, 
            persist=True, 
            tracker=self.tracker_type, 
            verbose=False
        )[0]
        
        tracked_objects = []
        
        # If no objects are detected, results.boxes might be empty or missing
        if not hasattr(results, 'boxes') or results.boxes is None or len(results.boxes) == 0:
            return tracked_objects
            
        for box in results.boxes:
            # Skip if the object doesn't have a tracking ID yet (often occurs on the very first frame an object appears)
            if box.id is None:
                continue
                
            cls_id = int(box.cls[0].item())
            
            if cls_id in self.allowed_classes:
                conf = float(box.conf[0].item())
                if conf >= conf_threshold:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    track_id = int(box.id[0].item())
                    
                    tracked_objects.append({
                        "track_id": track_id,
                        "class_name": self.allowed_classes[cls_id],
                        "confidence": conf,
                        "bbox": [x1, y1, x2, y2]
                    })
                    
        return tracked_objects
