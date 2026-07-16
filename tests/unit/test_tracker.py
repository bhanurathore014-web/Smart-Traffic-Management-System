import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from backend.core.tracker import VehicleTracker

@pytest.fixture
def mock_yolo_tracker():
    with patch("backend.core.tracker.YOLO") as mock:
        # Create a mock result simulating a tracking frame
        mock_result = MagicMock()
        
        # Mock class ID 2 (car) and confidence 0.8 with track ID 1
        mock_box1 = MagicMock()
        mock_box1.cls = [MagicMock(item=lambda: 2)]
        mock_box1.conf = [MagicMock(item=lambda: 0.8)]
        mock_box1.id = [MagicMock(item=lambda: 1)]
        mock_xyxy1 = MagicMock()
        mock_xyxy1.tolist.return_value = [10.0, 20.0, 100.0, 200.0]
        mock_box1.xyxy = [mock_xyxy1]
        
        # Mock class ID 5 (bus) with missing ID (should be skipped by tracking logic)
        mock_box2 = MagicMock()
        mock_box2.cls = [MagicMock(item=lambda: 5)]
        mock_box2.conf = [MagicMock(item=lambda: 0.9)]
        mock_box2.id = None
        mock_xyxy2 = MagicMock()
        mock_xyxy2.tolist.return_value = [5.0, 5.0, 50.0, 50.0]
        mock_box2.xyxy = [mock_xyxy2]
        
        mock_result.boxes = [mock_box1, mock_box2]
        
        mock_instance = MagicMock()
        # Mock the .track method instead of calling the model directly
        mock_instance.track.return_value = [mock_result]
        mock.return_value = mock_instance
        yield mock

def test_vehicle_tracker_init(mock_yolo_tracker, tmp_path):
    dummy_model = tmp_path / "dummy.pt"
    dummy_model.touch()
    
    tracker = VehicleTracker(str(dummy_model))
    assert tracker.allowed_classes[2] == "car"
    assert tracker.allowed_classes[5] == "bus"
    assert tracker.tracker_type == "bytetrack.yaml"
    
def test_vehicle_tracker_missing_weights():
    with pytest.raises(FileNotFoundError):
        VehicleTracker("non_existent_model.pt")

def test_vehicle_tracker_track(mock_yolo_tracker, tmp_path):
    dummy_model = tmp_path / "dummy.pt"
    dummy_model.touch()
    tracker = VehicleTracker(str(dummy_model))
    
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    tracked_objects = tracker.track(dummy_frame)
    
    # Should only return the car since the bus has no assigned tracking ID
    assert len(tracked_objects) == 1
    assert tracked_objects[0]["track_id"] == 1
    assert tracked_objects[0]["class_name"] == "car"
    assert tracked_objects[0]["confidence"] == 0.8
    assert tracked_objects[0]["bbox"] == [10.0, 20.0, 100.0, 200.0]
