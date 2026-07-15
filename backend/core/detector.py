import numpy as np
from pathlib import Path
from ultralytics import YOLO
from typing import List, Dict, Any

class VehicleDetector:
    def __init__(self, model_path: str = "models/weights/yolov8n.pt"):
        """
        Initializes the YOLOv8 vehicle detector.
        """
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model weights not found at {self.model_path}")
            
        self.model = YOLO(str(self.model_path))
        
        # COCO mapping for traffic vehicles
        # 2: car, 3: motorcycle, 5: bus, 7: truck
        self.allowed_classes = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

    def detect(self, frame: np.ndarray, conf_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Processes a BGR numpy array frame and returns bounding boxes 
        for detected traffic vehicles.
        """
        results = self.model(frame, verbose=False)[0]
        
        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0].item())
            if cls_id in self.allowed_classes:
                conf = float(box.conf[0].item())
                if conf >= conf_threshold:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    detections.append({
                        "class_name": self.allowed_classes[cls_id],
                        "confidence": conf,
                        "bbox": [x1, y1, x2, y2]
                    })
                    
        return detections
