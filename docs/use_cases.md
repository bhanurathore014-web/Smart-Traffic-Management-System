# Use Case Specifications
# AI-Powered Smart Traffic Management System

**Document Version:** 1.0  
**Phase:** 1 — Requirement Analysis  
**Date:** 2026-07-12

---

## Use Case Diagram (Textual Description)

```
                    ┌─────────────────────────────────────────────────────┐
                    │           Smart Traffic Management System            │
                    │                                                       │
  ┌──────────┐      │  ┌─────────────────┐   ┌──────────────────────┐     │
  │  Traffic  │────▶│  │  View Dashboard  │   │  Configure System    │     │
  │  Officer  │      │  └─────────────────┘   └──────────────────────┘     │
  └──────────┘      │                                                       │
                    │  ┌─────────────────┐   ┌──────────────────────┐     │
  ┌──────────┐      │  │  View ANPR Logs  │   │  Generate Reports    │     │
  │   Admin   │────▶│  └─────────────────┘   └──────────────────────┘     │
  └──────────┘      │                                                       │
                    │  ┌─────────────────┐   ┌──────────────────────┐     │
  ┌──────────┐      │  │  Emergency Alert │   │  Signal Override     │     │
  │  Camera   │────▶│  └─────────────────┘   └──────────────────────┘     │
  │  (System) │      │                                                       │
  └──────────┘      │  ┌─────────────────┐   ┌──────────────────────┐     │
                    │  │  Detect Vehicle  │   │  Count Vehicles      │     │
                    │  └─────────────────┘   └──────────────────────┘     │
                    │                                                       │
                    │  ┌─────────────────┐   ┌──────────────────────┐     │
                    │  │  Estimate Density│   │  Optimize Signal     │     │
                    │  └─────────────────┘   └──────────────────────┘     │
                    └─────────────────────────────────────────────────────┘
```

---

## UC-01: Process Video Feed

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-01 |
| **Name** | Process Video Feed |
| **Actor** | System (automated), Camera |
| **Priority** | Critical |
| **Description** | The system continuously reads frames from a video source and processes them through the detection and tracking pipeline. |

### Preconditions
- Video file or RTSP stream is accessible
- YOLOv8 model weights are loaded
- Database connection is established

### Main Flow (Happy Path)
1. System opens the video source (file/stream)
2. System reads a frame from the source
3. Frame is preprocessed (resize, normalize)
4. YOLOv8 model performs inference on the frame
5. Detected bounding boxes are passed to ByteTrack
6. ByteTrack assigns/updates Track IDs
7. System checks if any tracked vehicle crosses a counting line
8. System updates vehicle counts per lane
9. System estimates traffic density per lane
10. System triggers the signal optimization algorithm
11. Processed frame (with overlays) is stored for dashboard display
12. Detection data is written to the database
13. Repeat from step 2

### Alternative Flow
- **2a. Video source is unavailable:** Log error, retry 3 times, then alert dashboard
- **4a. No detections in frame:** Skip steps 5–10, update empty frame
- **8a. Vehicle re-enters lane:** Count is incremented again (configurable option to prevent double-counting)

### Postconditions
- Vehicle counts, density, and signal timings are updated
- Frame with bounding boxes is available for display
- Detection event is stored in DB

---

## UC-02: Adaptive Signal Timing

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-02 |
| **Name** | Calculate Adaptive Signal Timing |
| **Actor** | System (automated) |
| **Priority** | Critical |

### Preconditions
- Traffic density values are available for all lanes
- Previous signal state is known
- No active emergency override

### Main Flow
1. System retrieves current density score for each lane (0.0–1.0)
2. System applies the weighted allocation formula:
   - `raw_green[i] = (density[i] / sum(density)) × total_cycle_time`
3. System applies min/max bounds:
   - `green[i] = clamp(raw_green[i], MIN_GREEN=10, MAX_GREEN=90)`
4. System enforces fairness: any lane waiting > MAX_WAIT cycles gets bumped to minimum
5. System outputs a new signal schedule `[lane1_green, lane2_green, lane3_green, lane4_green]`
6. Schedule is stored in the database
7. Signal controller applies the new schedule

### Example
```
Densities:   Lane1=0.75, Lane2=0.10, Lane3=0.55, Lane4=0.08
Raw allocation (total=150s): Lane1=73s, Lane2=10s, Lane3=54s, Lane4=13s
After clamping (min=10, max=90): Lane1=73s, Lane2=10s, Lane3=54s, Lane4=13s
Output: [73, 10, 54, 13]
```

### Alternative Flow
- **1a. All densities are 0:** Assign equal minimum green time to all lanes
- **3a. Sum exceeds total cycle time:** Proportionally scale down all green times

---

## UC-03: Emergency Vehicle Priority

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-03 |
| **Name** | Emergency Vehicle Priority Override |
| **Actor** | System (automated) |
| **Priority** | Critical |

### Preconditions
- System is actively processing video frames
- YOLOv8 emergency vehicle classes are enabled (ambulance, fire truck, police)

### Main Flow
1. System detects a vehicle classified as ambulance/fire_truck/police_car with confidence ≥ 0.6
2. System identifies the lane containing the emergency vehicle
3. System immediately pauses the current signal cycle
4. System sets the emergency lane to GREEN (immediately)
5. System sets all other lanes to RED
6. Emergency event is logged (vehicle type, lane, timestamp)
7. Alert is sent to dashboard (visual + text notification)
8. System monitors the emergency vehicle's position
9. When the emergency vehicle exits the ROI (disappears from that lane), the override ends
10. System resumes the normal adaptive signal cycle from where it paused

### Alternative Flow
- **9a. Emergency vehicle is not detected for 30 consecutive frames:** Override ends automatically
- **1a. Multiple emergency vehicles in different lanes:** Priority given to first-detected; second vehicle queued

### Postconditions
- Emergency event record created in database
- Normal signal cycle resumed
- Alert cleared from dashboard

---

## UC-04: Number Plate Recognition

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-04 |
| **Name** | Automatic Number Plate Recognition |
| **Actor** | System (automated) |
| **Priority** | High |

### Main Flow
1. Vehicle is detected with bounding box by YOLOv8
2. System crops the vehicle ROI from the frame
3. A secondary YOLO model (or heuristic) detects the plate sub-region within the vehicle ROI
4. Plate region is cropped and preprocessed (grayscale, contrast enhance, denoise)
5. EasyOCR performs text recognition on the preprocessed plate image
6. Recognized text is post-processed (remove spaces, standardize format)
7. Plate text is validated against Indian plate format regex
8. Plate record is stored: `{vehicle_id, plate_text, confidence, timestamp, lane, frame_image_path}`
9. Plate appears in ANPR log on dashboard

### Alternative Flow
- **3a. Plate sub-region not detected:** Log as "plate_not_found"; skip OCR
- **6a. OCR confidence < 0.5:** Store as "low_confidence"; flag for manual review
- **7a. Plate format invalid:** Store raw text with "format_invalid" flag

---

## UC-05: View Dashboard

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-05 |
| **Name** | View Analytics Dashboard |
| **Actor** | Traffic Officer, Admin |
| **Priority** | High |

### Main Flow
1. User opens the Streamlit dashboard in a web browser
2. Dashboard loads the live camera feed widget
3. Dashboard queries the API for current traffic state (counts, density, signal status)
4. Charts auto-refresh every 2 seconds
5. User navigates between dashboard tabs:
   - **Overview** — live feed + real-time metrics
   - **Analytics** — hourly/daily charts, peak hour analysis
   - **ANPR Logs** — searchable plate log table
   - **Signal History** — timing chart over time
   - **Emergency Alerts** — event log
6. User can apply date/time filters on historical charts

### Alternative Flow
- **3a. API is unavailable:** Dashboard shows "System Offline" banner
- **2a. Live feed not available:** Dashboard shows placeholder image

---

## UC-06: Generate Traffic Report

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-06 |
| **Name** | Generate Traffic Analytics Report |
| **Actor** | Admin |
| **Priority** | Medium |

### Main Flow
1. Admin selects "Generate Report" in the dashboard
2. Admin selects report type: Hourly / Daily / Weekly
3. Admin selects date range
4. System queries aggregated data from the database
5. System generates a PDF/CSV report with:
   - Total vehicle count by type
   - Peak congestion hours
   - Average signal timing per lane
   - Emergency events summary
   - Top 10 most frequent plates
6. Report is downloaded by the admin

---

*End of Use Cases — Phase 1 Deliverable 2 of 3*
