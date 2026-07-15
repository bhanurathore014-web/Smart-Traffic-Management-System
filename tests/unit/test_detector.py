import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from backend.core.detector import VehicleDetector

@pytest.fixture
def mock_yolo():
    with patch("backend.core.detector.YOLO") as mock:
        # Create a mock result
        mock_result = MagicMock()
        
        # Mock class ID 2 (car) and confidence 0.8
        mock_box1 = MagicMock()
        mock_box1.cls = [MagicMock(item=lambda: 2)]
        mock_box1.conf = [MagicMock(item=lambda: 0.8)]
        mock_xyxy1 = MagicMock()
        mock_xyxy1.tolist.return_value = [10.0, 20.0, 100.0, 200.0]
        mock_box1.xyxy = [mock_xyxy1]
        
        # Mock class ID 0 (person) to test filtering
        mock_box2 = MagicMock()
        mock_box2.cls = [MagicMock(item=lambda: 0)]
        mock_box2.conf = [MagicMock(item=lambda: 0.9)]
        mock_xyxy2 = MagicMock()
        mock_xyxy2.tolist.return_value = [5.0, 5.0, 50.0, 50.0]
        mock_box2.xyxy = [mock_xyxy2]
        
        # Mock class ID 3 (motorcycle) but low confidence
        mock_box3 = MagicMock()
        mock_box3.cls = [MagicMock(item=lambda: 3)]
        mock_box3.conf = [MagicMock(item=lambda: 0.1)] # below 0.3 threshold
        mock_xyxy3 = MagicMock()
        mock_xyxy3.tolist.return_value = [0.0, 0.0, 10.0, 10.0]
        mock_box3.xyxy = [mock_xyxy3]
        
        mock_result.boxes = [mock_box1, mock_box2, mock_box3]
        
        mock_instance = MagicMock()
        mock_instance.return_value = [mock_result]
        mock.return_value = mock_instance
        yield mock

def test_vehicle_detector_init(mock_yolo, tmp_path):
    dummy_model = tmp_path / "dummy.pt"
    dummy_model.touch()
    
    detector = VehicleDetector(str(dummy_model))
    assert detector.allowed_classes[2] == "car"
    assert detector.allowed_classes[5] == "bus"
    assert detector.allowed_classes[7] == "truck"
    
def test_vehicle_detector_missing_weights():
    with pytest.raises(FileNotFoundError):
        VehicleDetector("non_existent_model.pt")

def test_vehicle_detector_detect(mock_yolo, tmp_path):
    dummy_model = tmp_path / "dummy.pt"
    dummy_model.touch()
    detector = VehicleDetector(str(dummy_model))
    
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    detections = detector.detect(dummy_frame)
    
    # Should only return the car (person is filtered out, motorcycle is low confidence)
    assert len(detections) == 1
    assert detections[0]["class_name"] == "car"
    assert detections[0]["confidence"] == 0.8
    assert detections[0]["bbox"] == [10.0, 20.0, 100.0, 200.0]
