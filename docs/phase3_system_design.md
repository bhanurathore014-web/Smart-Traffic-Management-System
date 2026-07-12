# System Design Document
# AI-Powered Smart Traffic Management System

**Document Version:** 1.0  
**Phase:** 3 — System Design  
**Date:** 2026-07-12

---

## Table of Contents

1. [System Architecture Diagram](#1-system-architecture-diagram)
2. [Data Flow Diagram (DFD)](#2-data-flow-diagram)
3. [Class Diagram](#3-class-diagram)
4. [Sequence Diagram](#4-sequence-diagram)
5. [Entity-Relationship (ER) Diagram](#5-entity-relationship-diagram)
6. [Use Case Diagram](#6-use-case-diagram)
7. [Activity Diagram — Emergency Override](#7-activity-diagram)
8. [Deployment Diagram](#8-deployment-diagram)

---

## 1. System Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                  AI-Powered Smart Traffic Management System                  ║
║                          High-Level Architecture                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                          INPUT LAYER                                     │
  │                                                                           │
  │   [CCTV Camera 1]  [CCTV Camera 2]  [CCTV Camera 3]  [CCTV Camera 4]   │
  │         │                │                │                │              │
  │    Lane 1 Feed      Lane 2 Feed      Lane 3 Feed      Lane 4 Feed        │
  └──────────────────────────┬──────────────────────────────────────────────┘
                             │  Video Frames
                             ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                       CORE PROCESSING ENGINE                             │
  │                                                                           │
  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌────────────┐  │
  │  │  Frame      │   │  YOLOv8     │   │  ByteTrack  │   │  Vehicle   │  │
  │  │  Preprocessor│──▶│  Detector   │──▶│  Tracker    │──▶│  Counter   │  │
  │  └─────────────┘   └─────────────┘   └─────────────┘   └─────┬──────┘  │
  │                                                                │          │
  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐         │          │
  │  │  ANPR       │   │  Emergency  │   │  Density    │◀────────┘          │
  │  │  Pipeline   │   │  Detector   │   │  Estimator  │                    │
  │  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘                    │
  │         │                 │                  │                            │
  │         └─────────────────┼──────────────────┘                           │
  │                           ▼                                               │
  │                  ┌─────────────────┐                                     │
  │                  │  Signal         │                                     │
  │                  │  Controller     │                                     │
  │                  └────────┬────────┘                                     │
  └───────────────────────────┼─────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
  ┌──────────────────┐ ┌───────────┐ ┌──────────────────┐
  │   FastAPI        │ │ Database  │ │  Event Logger    │
  │   Backend        │ │ Layer     │ │  (Loguru)        │
  │   (REST API)     │ │           │ └──────────────────┘
  └────────┬─────────┘ │ PostgreSQL│
           │           │ / SQLite  │
           │           └─────┬─────┘
           │                 │
           └────────┬────────┘
                    ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                        PRESENTATION LAYER                                │
  │                                                                           │
  │          ┌────────────────────────────────────────┐                     │
  │          │         Streamlit Dashboard             │                     │
  │          │                                         │                     │
  │          │  [Live Feed] [Metrics] [Charts]         │                     │
  │          │  [ANPR Log] [Alerts]  [Signal Status]   │                     │
  │          └────────────────────────────────────────┘                     │
  └─────────────────────────────────────────────────────────────────────────┘
```

### Architecture Layers

| Layer | Components | Responsibility |
|-------|-----------|----------------|
| **Input** | CCTV feeds, video files, RTSP streams | Provide raw video data |
| **Processing** | YOLOv8, ByteTrack, Counter, Density, Emergency, ANPR, Signal | Core AI computation |
| **API** | FastAPI + Pydantic + Uvicorn | REST endpoints, data validation |
| **Persistence** | PostgreSQL/SQLite + SQLAlchemy + Alembic | Data storage and migrations |
| **Presentation** | Streamlit + Plotly | Interactive analytics dashboard |
| **Infrastructure** | Docker, Docker Compose, Loguru | Deployment and observability |

---

## 2. Data Flow Diagram

### Level 0 — Context DFD

```
                        ┌──────────────────────────────────┐
  [Traffic Officer] ───▶│                                  │───▶ [Signal Display]
                        │                                  │
  [Admin User]     ───▶│   AI Traffic Management System   │───▶ [Dashboard View]
                        │                                  │
  [CCTV Camera]    ───▶│                                  │───▶ [ANPR Alert]
                        │                                  │
  [Config Files]   ───▶│                                  │───▶ [Traffic Reports]
                        └──────────────────────────────────┘
```

### Level 1 — System DFD

```
                    Video Frames
 [Camera Feed] ──────────────────▶ ┌──────────────┐
                                    │  1.0 Frame   │
                                    │  Preprocessor│
                                    └──────┬───────┘
                                           │ Normalized Frame
                                           ▼
                                    ┌──────────────┐         Detections
                                    │  2.0 YOLOv8  │──────────────────▶ ┌──────────────┐
                                    │  Detector    │                     │  3.0         │
                                    └──────────────┘                     │  ByteTrack   │
                                                                          └──────┬───────┘
                             ┌──────────────────────────────────────────────────┘
                             │ Tracked Vehicles (ID, bbox, class)
              ┌──────────────┼──────────────────┐
              ▼              ▼                  ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │  4.0 Vehicle │  │  5.0 ANPR    │  │  6.0 Emerg.  │
  │  Counter     │  │  Pipeline    │  │  Detector    │
  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │ Count/Lane      │ Plate Text        │ Alert Flag
         ▼                 ▼                   ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │  7.0 Density │  │  [DB: Plates]│  │  8.0 Signal  │
  │  Estimator   │  └──────────────┘  │  Controller  │
  └──────┬───────┘                    └──────┬───────┘
         │ Density/Lane                       │ Signal Schedule
         └──────────────────┐    ┌────────────┘
                            ▼    ▼
                     ┌──────────────┐     ┌───────────────┐
                     │  [DB: All    │     │  9.0 FastAPI  │
                     │   Tables]    │────▶│  Server       │
                     └──────────────┘     └──────┬────────┘
                                                 │ JSON Responses
                                                 ▼
                                          ┌──────────────┐
                                          │  10.0        │
                                          │  Streamlit   │
                                          │  Dashboard   │
                                          └──────────────┘
```

### Data Store Dictionary

| Store | Contents | Access Pattern |
|-------|----------|----------------|
| D1 — Vehicles | detections, tracks, timestamps | Write: every frame; Read: dashboard |
| D2 — Traffic | density, speed, occupancy per lane | Write: every 5s; Read: signal algo + dashboard |
| D3 — Signals | state, duration, timestamps | Write: every cycle change; Read: dashboard |
| D4 — Emergency | event type, lane, duration | Write: on event; Read: dashboard alerts |
| D5 — Plates | recognized text, confidence, image | Write: on recognition; Read: ANPR log |
| D6 — Analytics | aggregated hourly/daily stats | Write: every hour; Read: reports |

---

## 3. Class Diagram

```
┌────────────────────────────────────┐
│          VideoProcessor            │
├────────────────────────────────────┤
│ - source: str                      │
│ - detector: VehicleDetector        │
│ - tracker: ByteTracker             │
│ - counter: VehicleCounter          │
│ - density: DensityEstimator        │
│ - signal: SignalController         │
│ - emergency: EmergencyDetector     │
│ - anpr: ANPRPipeline               │
│ - db: DatabaseManager              │
│ - logger: Logger                   │
├────────────────────────────────────┤
│ + start() : None                   │
│ + stop() : None                    │
│ + process_frame(frame) : Frame     │
│ + get_stats() : dict               │
└────────────────┬───────────────────┘
                 │ uses
    ┌────────────┼──────────────────────────────────┐
    │            │                                   │
    ▼            ▼                                   ▼
┌──────────┐  ┌───────────────────┐  ┌──────────────────────┐
│ Vehicle  │  │  VehicleDetector  │  │   ByteTracker         │
│ Detector │  ├───────────────────┤  ├──────────────────────┤
├──────────┤  │ - model: YOLO     │  │ - tracker: BYTETracker│
│ - model  │  │ - conf_threshold  │  │ - max_age: int        │
│ - conf   │  │ - iou_threshold   │  │ - min_hits: int       │
│ - classes│  ├───────────────────┤  ├──────────────────────┤
├──────────┤  │ + detect(frame)   │  │ + update(detections) │
│+ detect()│  │ + load_model()    │  │ + get_tracks()       │
└──────────┘  │ + filter_classes()│  └──────────────────────┘
              └───────────────────┘

┌────────────────────────┐   ┌────────────────────────┐
│   VehicleCounter       │   │   DensityEstimator      │
├────────────────────────┤   ├────────────────────────┤
│ - lanes: dict[int,Lane]│   │ - weights: dict         │
│ - counting_lines: list │   │ - thresholds: dict      │
│ - counted_ids: set     │   │ - history: deque        │
├────────────────────────┤   ├────────────────────────┤
│ + update(tracks)       │   │ + estimate(lane) float  │
│ + get_counts() dict    │   │ + classify(score) str   │
│ + reset_counts()       │   │ + smooth(window) float  │
└────────────────────────┘   └────────────────────────┘

┌────────────────────────────────┐
│      SignalController           │
├────────────────────────────────┤
│ - current_phase: int           │
│ - state: SignalState           │
│ - schedule: list[GreenTime]    │
│ - config: SignalConfig         │
│ - emergency_override: bool     │
├────────────────────────────────┤
│ + compute_schedule(density)    │
│ + get_current_state() dict     │
│ + trigger_emergency(lane) None │
│ + resume_normal() None         │
│ + tick(delta_time) None        │
└────────────────────────────────┘

┌────────────────────────┐   ┌────────────────────────┐
│  EmergencyDetector     │   │    ANPRPipeline         │
├────────────────────────┤   ├────────────────────────┤
│ - classes: list[str]   │   │ - plate_detector: YOLO  │
│ - conf_threshold: float│   │ - ocr_primary: EasyOCR │
│ - confirm_frames: int  │   │ - ocr_fallback: Paddle  │
│ - detection_buffer     │   │ - preprocessor          │
├────────────────────────┤   ├────────────────────────┤
│ + detect(tracks) bool  │   │ + recognize(frame,bbox) │
│ + get_alert() dict     │   │ + preprocess(crop) img  │
│ + confirm() bool       │   │ + validate_plate(text)  │
└────────────────────────┘   └────────────────────────┘

┌────────────────────────────────────────┐
│           DatabaseManager              │
├────────────────────────────────────────┤
│ - engine: Engine                       │
│ - session_factory: sessionmaker        │
├────────────────────────────────────────┤
│ + save_detection(d: Detection) None    │
│ + save_traffic(t: TrafficRecord) None  │
│ + save_signal(s: SignalRecord) None    │
│ + save_emergency(e: EmergencyEvent)    │
│ + save_plate(p: PlateRecord) None      │
│ + get_stats(hours: int) dict           │
└────────────────────────────────────────┘

┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Detection  │     │  TrackResult │     │  LaneState   │
├─────────────┤     ├──────────────┤     ├──────────────┤
│ bbox: tuple │     │ track_id:int │     │ lane_id: int │
│ class_id:int│     │ bbox: tuple  │     │ count: int   │
│ confidence  │     │ class_id:int │     │ density:float│
│ frame_id:int│     │ confidence   │     │ speed: float │
│ timestamp   │     │ is_confirmed │     │ signal:str   │
└─────────────┘     └──────────────┘     └──────────────┘
```

---

## 4. Sequence Diagram

### SD-01: Normal Vehicle Detection to Signal Update

```
VideoProcessor  Detector  Tracker  Counter  Density  SignalCtrl  Database  Dashboard
     │              │         │        │        │         │           │          │
     │──read_frame()▶         │        │        │         │           │          │
     │◀──frame─────           │        │        │         │           │          │
     │                        │        │        │         │           │          │
     │──detect(frame)────────▶│        │        │         │           │          │
     │◀──[bbox,cls,conf]──────│        │        │         │           │          │
     │                        │        │        │         │           │          │
     │──update(detections)─────────────▶        │         │           │          │
     │◀──[tracked_objects]─────────────         │         │           │          │
     │                        │        │        │         │           │          │
     │──update(tracks)─────────────────────────▶│         │           │          │
     │◀──{lane_counts}─────────────────────────         │           │          │
     │                        │        │        │         │           │          │
     │──estimate(lane_counts)──────────────────────────▶ │           │          │
     │◀──{density_scores}─────────────────────────────── │           │          │
     │                        │        │        │         │           │          │
     │──compute_schedule(density)───────────────────────────────────▶│         │
     │──tick(delta_t)────────────────────────────────────────────────▶│        │
     │◀──{signal_state}──────────────────────────────────────────────         │
     │                        │        │        │         │           │          │
     │──save_all(data)────────────────────────────────────────────────────────▶ │
     │◀──ok───────────────────────────────────────────────────────────────────  │
     │                        │        │        │         │           │          │
     │──broadcast_update()─────────────────────────────────────────────────────▶│
     │                        │        │        │         │           │          │
     │── [repeat next frame]  │        │        │         │           │          │
```

### SD-02: Emergency Vehicle Override

```
Detector    EmergencyDet   SignalCtrl   Database   Dashboard
    │              │              │          │          │
    │──detections──▶              │          │          │
    │              │              │          │          │
    │      detect_emergency(tracks)          │          │
    │              │──check confidence──     │          │
    │              │──frame_count >= 3 ?     │          │
    │              │  [YES → confirmed]      │          │
    │              │              │          │          │
    │              │──trigger_emergency(lane)▶          │
    │              │              │          │          │
    │              │         set all RED     │          │
    │              │         set lane GREEN  │          │
    │              │              │          │          │
    │              │──────────────────────────────────save_emergency()
    │              │              │          │          │
    │              │──────────────────────────────────send_alert()
    │              │              │          │          │
    │      [monitor vehicle position]        │          │
    │      [vehicle exits ROI]               │          │
    │              │              │          │          │
    │              │──resume_normal()────────▶          │
    │              │              │          │          │
    │              │──────────────────────────────────clear_alert()
```

---

## 5. Entity-Relationship (ER) Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      DATABASE ENTITY RELATIONSHIPS                        │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐          ┌─────────────────────┐
│     cameras     │          │      vehicles        │
├─────────────────┤          ├─────────────────────┤
│ PK camera_id    │1        N│ PK vehicle_id        │
│    camera_name  │──────────│ FK camera_id         │
│    lane_id      │          │    track_id           │
│    location     │          │    class_name         │
│    rtsp_url     │          │    confidence         │
│    is_active    │          │    bbox_x1,y1,x2,y2   │
│    created_at   │          │    frame_id            │
└─────────────────┘          │    detected_at        │
                             │    speed_kmh           │
                             └──────────┬──────────────┘
                                        │1
                              ┌─────────┘
                              │
                       ┌──────▼──────────────┐
                       │   number_plates      │
                       ├─────────────────────┤
                       │ PK plate_id          │
                       │ FK vehicle_id        │
                       │    plate_text        │
                       │    ocr_confidence    │
                       │    ocr_engine        │
                       │    is_valid          │
                       │    image_path        │
                       │    recognized_at     │
                       └─────────────────────┘

┌─────────────────────┐          ┌─────────────────────┐
│   traffic_records    │          │   signal_records     │
├─────────────────────┤          ├─────────────────────┤
│ PK record_id         │          │ PK signal_id         │
│ FK camera_id         │          │ FK camera_id         │
│    lane_id           │          │    lane_id            │
│    vehicle_count     │          │    signal_state       │
│    density_score     │          │    green_duration     │
│    density_level     │          │    yellow_duration    │
│    occupancy_ratio   │          │    red_duration       │
│    avg_speed_kmh     │          │    cycle_number       │
│    timestamp         │          │    is_emergency       │
└─────────────────────┘          │    started_at         │
                                 │    ended_at           │
                                 └─────────────────────┘

┌─────────────────────┐          ┌─────────────────────┐
│  emergency_events    │          │   analytics_hourly   │
├─────────────────────┤          ├─────────────────────┤
│ PK event_id          │          │ PK analytics_id      │
│ FK camera_id         │          │ FK camera_id         │
│    vehicle_type      │          │    lane_id            │
│    lane_id           │          │    hour_bucket        │
│    confidence        │          │    total_vehicles     │
│    override_start    │          │    cars_count         │
│    override_end      │          │    buses_count        │
│    duration_seconds  │          │    trucks_count       │
│    is_confirmed      │          │    motorcycles_count  │
│    plate_text        │          │    avg_density        │
└─────────────────────┘          │    avg_signal_green   │
                                 │    peak_count         │
┌─────────────────────┐          │    created_at         │
│   system_config     │          └─────────────────────┘
├─────────────────────┤
│ PK config_id         │
│    key               │  ◀── Stores: min_green, max_green,
│    value             │             total_cycle, conf_threshold,
│    value_type        │             density_weights, etc.
│    description       │
│    updated_at        │
└─────────────────────┘
```

### Relationships Summary

| Relationship | Type | FK Location |
|-------------|------|-------------|
| camera → vehicles | 1:N | vehicles.camera_id |
| vehicle → number_plates | 1:1 | number_plates.vehicle_id |
| camera → traffic_records | 1:N | traffic_records.camera_id |
| camera → signal_records | 1:N | signal_records.camera_id |
| camera → emergency_events | 1:N | emergency_events.camera_id |
| camera → analytics_hourly | 1:N | analytics_hourly.camera_id |

---

## 6. Use Case Diagram

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                  AI Traffic Management System Boundary                    ║
║                                                                            ║
║   ┌──────────────────────────────────────────────────────────────────┐   ║
║   │                                                                    │   ║
║   │  (Process Video Feed) ←── «include» ── (Detect Vehicles)         │   ║
║   │         ↑                                      ↓                  │   ║
║   │      «include»                          (Track Vehicles)          │   ║
║   │         │                                      ↓                  │   ║
║   │  (Count Vehicles) ──────────────▶ (Estimate Traffic Density)     │   ║
║   │                                               ↓                  │   ║
║   │                                  (Optimize Signal Timing)         │   ║
║   │                                                                    │   ║
║   │  (Detect Emergency) ─── «extend» ──▶ (Trigger Override)          │   ║
║   │                                            ↓                      │   ║
║   │                                    (Resume Normal Cycle)          │   ║
║   │                                                                    │   ║
║   │  (Recognize Number Plate) ────▶ (Store Plate Record)             │   ║
║   │                                                                    │   ║
║   │  (View Dashboard) ←── «include» ── (View Live Feed)              │   ║
║   │         │                          (View Charts)                  │   ║
║   │         │                          (View ANPR Log)                │   ║
║   │         │                          (View Alerts)                  │   ║
║   │                                                                    │   ║
║   │  (Generate Report) ────▶ (Export CSV / PDF)                      │   ║
║   │                                                                    │   ║
║   │  (Configure System) ────▶ (Update Thresholds)                    │   ║
║   │                           (Manage Cameras)                        │   ║
║   └──────────────────────────────────────────────────────────────────┘   ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝

     [Camera]                 [Traffic Officer]                [Admin]
        │                           │                             │
        │                      (View Dashboard)         (Configure System)
        │                      (View Alerts)            (Generate Report)
        │                      (View ANPR Log)          (Manage Cameras)
(Process Video Feed)
(Detect Emergency)
(Recognize Number Plate)
```

---

## 7. Activity Diagram

### AD-01: Emergency Vehicle Override Flow

```
        [START]
           │
           ▼
   ┌───────────────┐
   │ Process Frame │
   └──────┬────────┘
          │
          ▼
   ┌───────────────────────────┐
   │ Run YOLOv8 Detection      │
   └──────────────┬────────────┘
                  │
          ┌───────┴──────────┐
          │                  │
          ▼ YES              ▼ NO
   ┌──────────────┐    ┌──────────────────┐
   │ Emergency    │    │ Normal Detection  │
   │ Class Found? │    │ Processing        │
   └──────┬───────┘    └──────────────────┘
          │
          ▼
   ┌─────────────────────────┐
   │ Confidence >= 0.60?     │
   └──────┬──────┬───────────┘
          │YES   │NO
          │      ▼
          │  [Discard / Continue Normal]
          ▼
   ┌─────────────────────────┐
   │ Increment Frame Counter  │
   │ frame_count += 1         │
   └──────┬──────────────────┘
          │
          ▼
   ┌─────────────────────────┐
   │ frame_count >= 3?       │
   └──────┬──────┬───────────┘
          │YES   │NO
          │      ▼
          │  [Continue accumulating frames]
          ▼
   ┌─────────────────────────┐
   │ CONFIRM EMERGENCY EVENT  │
   └──────┬──────────────────┘
          │
          ▼
   ┌─────────────────────────┐
   │ Identify Emergency Lane  │
   └──────┬──────────────────┘
          │
          ▼
   ┌─────────────────────────┐   ┌──────────────────────┐
   │ Pause Normal Signal      │──▶│ Log Event to DB      │
   │ Cycle                   │   │ Send Dashboard Alert  │
   └──────┬──────────────────┘   └──────────────────────┘
          │
          ▼
   ┌──────────────────────────────────────────┐
   │ Set Emergency Lane → GREEN               │
   │ Set All Other Lanes → RED                │
   └──────┬───────────────────────────────────┘
          │
          ▼
   ┌─────────────────────────────────────────────┐
   │ Monitor: Vehicle still in ROI?               │
   │ OR absence_frames >= 30?                     │
   └──────┬──────────────────────────────────────┘
          │ NO (still present)
          │◀────────────────────────────────────┐
          │                                     │
          │ YES (vehicle exited or timeout)     │
          ▼                                     │
   ┌─────────────────────────┐         [Monitor Loop]
   │ End Override             │
   │ Resume Normal Cycle      │
   └──────┬──────────────────┘
          │
          ▼
   ┌─────────────────────────┐
   │ Update DB: event ended   │
   │ Clear Dashboard Alert    │
   └──────┬──────────────────┘
          │
          ▼
        [END]
```

### AD-02: ANPR Recognition Flow

```
   [Tracked Vehicle Detected]
           │
           ▼
   ┌──────────────────────┐
   │ Crop Vehicle ROI     │
   │ from Frame           │
   └──────┬───────────────┘
          │
          ▼
   ┌──────────────────────┐
   │ Plate Sub-Region     │
   │ Detection (YOLO/     │
   │ Heuristic)           │
   └──────┬───────┬───────┘
          │FOUND  │NOT FOUND
          │       ▼
          │   [Log: plate_not_found → skip]
          ▼
   ┌──────────────────────┐
   │ Preprocess Plate Crop│
   │ (grayscale, CLAHE,   │
   │  denoise, morph)     │
   └──────┬───────────────┘
          │
          ▼
   ┌──────────────────────┐
   │ EasyOCR Inference    │
   └──────┬───────────────┘
          │
          ▼
   ┌──────────────────────┐
   │ OCR Confidence > 0.5?│
   └──────┬───────┬───────┘
          │YES    │NO
          │       ▼
          │   ┌──────────────────┐
          │   │ PaddleOCR        │
          │   │ Fallback         │
          │   └──────┬───────────┘
          │          │
          └──────────┘
                │
                ▼
   ┌──────────────────────┐
   │ Validate Indian Plate│
   │ Regex Format         │
   └──────┬───────┬───────┘
          │VALID  │INVALID
          │       ▼
          │  [Store raw text with format_invalid flag]
          ▼
   ┌──────────────────────┐
   │ Store Plate Record   │
   │ {text, confidence,   │
   │  vehicle_id, time}   │
   └──────────────────────┘
```

---

## 8. Deployment Diagram

```
╔══════════════════════════════════════════════════════════════════════════╗
║                         DOCKER COMPOSE ENVIRONMENT                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  ┌──────────────────────────────────────────────────────────────────┐    ║
║  │                    Host Machine (Linux/Mac/Win)                    │    ║
║  │                                                                    │    ║
║  │  ┌─────────────────────┐   ┌────────────────────────────────┐   │    ║
║  │  │  Container:          │   │  Container:                     │   │    ║
║  │  │  smart-traffic-app  │   │  smart-traffic-db               │   │    ║
║  │  │                     │   │                                 │   │    ║
║  │  │  ┌───────────────┐  │   │  ┌─────────────────────────┐  │   │    ║
║  │  │  │ FastAPI       │  │   │  │ PostgreSQL 16            │  │   │    ║
║  │  │  │ :8000         │  │   │  │ :5432                   │  │   │    ║
║  │  │  └───────────────┘  │   │  │                         │  │   │    ║
║  │  │  ┌───────────────┐  │   │  │  DB: smart_traffic      │  │   │    ║
║  │  │  │ Streamlit     │  │   │  │  User: traffic_user     │  │   │    ║
║  │  │  │ :8501         │  │   │  └─────────────────────────┘  │   │    ║
║  │  │  └───────────────┘  │   │                                 │   │    ║
║  │  │  ┌───────────────┐  │   │  Volume: postgres_data:/var/   │   │    ║
║  │  │  │ YOLOv8 Model  │  │   │          lib/postgresql/data   │   │    ║
║  │  │  │ ByteTrack     │  │   └────────────────────────────────┘   │    ║
║  │  │  │ EasyOCR       │  │                                         │    ║
║  │  │  └───────────────┘  │   ┌────────────────────────────────┐   │    ║
║  │  │                     │   │  Container:                     │   │    ║
║  │  │  Volume: ./videos   │   │  smart-traffic-redis (optional) │   │    ║
║  │  │  Volume: ./outputs  │   │  :6379  (caching)               │   │    ║
║  │  │  Volume: ./logs     │   └────────────────────────────────┘   │    ║
║  │  │  Volume: ./models   │                                         │    ║
║  │  └─────────────────────┘                                         │    ║
║  │                                                                    │    ║
║  │  Port Mappings:                                                    │    ║
║  │    8000 → FastAPI REST API                                         │    ║
║  │    8501 → Streamlit Dashboard                                      │    ║
║  │    5432 → PostgreSQL (internal only)                               │    ║
║  └──────────────────────────────────────────────────────────────────┘    ║
║                                                                            ║
╠══════════════════════════════════════════════════════════════════════════╣
║                    OPTIONAL: CLOUD DEPLOYMENT (Render / Railway)           ║
║                                                                            ║
║   [Railway PostgreSQL]  ←──── [Render Web Service (Docker)]               ║
║           DB URL                FastAPI + Streamlit                        ║
║                                 (Single container)                         ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### Docker Services Summary

| Service | Image | Ports | Volumes | Dependencies |
|---------|-------|-------|---------|-------------|
| `smart-traffic-app` | Custom (Python 3.12) | 8000, 8501 | videos, outputs, logs, models | db |
| `smart-traffic-db` | postgres:16-alpine | 5432 (internal) | postgres_data | — |
| `smart-traffic-redis` | redis:7-alpine | 6379 (internal) | — | — |

### Environment Variables

| Variable | Used By | Example |
|----------|---------|---------|
| `DATABASE_URL` | FastAPI, SQLAlchemy | `postgresql://user:pass@db:5432/smart_traffic` |
| `YOLO_MODEL_PATH` | VehicleDetector | `/app/models/yolov8s.pt` |
| `CONF_THRESHOLD` | Detector | `0.5` |
| `MIN_GREEN_TIME` | SignalController | `10` |
| `MAX_GREEN_TIME` | SignalController | `90` |
| `TOTAL_CYCLE_TIME` | SignalController | `150` |
| `LOG_LEVEL` | Loguru | `INFO` |
| `VIDEO_SOURCE` | VideoProcessor | `/app/videos/traffic.mp4` |

---

## 9. Module Interaction Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MODULE DEPENDENCY GRAPH                            │
│                                                                       │
│  config/ ──────────────────────────────────────────────────────┐    │
│                                                                  │    │
│  [VideoProcessor]                                                │    │
│       │                                                          │    │
│       ├──▶ [VehicleDetector]   ←── models/yolov8s.pt           │    │
│       │          │                                              │    │
│       ├──▶ [ByteTracker]  ◀── detections from Detector         │    │
│       │          │                                              │    │
│       ├──▶ [VehicleCounter]  ◀── tracks from Tracker           │    │
│       │          │                                              │    │
│       ├──▶ [DensityEstimator]  ◀── counts from Counter         │    │
│       │          │                                              │    │
│       ├──▶ [SignalController]  ◀── density from Estimator      │    │
│       │          │                                              │    │
│       ├──▶ [EmergencyDetector]  ◀── tracks from Tracker        │    │
│       │          │──▶ [SignalController.trigger_emergency()]    │    │
│       │                                                         │    │
│       ├──▶ [ANPRPipeline]  ◀── tracks from Tracker             │    │
│       │                                                         │    │
│       └──▶ [DatabaseManager]  ◀── data from all modules        │    │
│                  │                                              │    │
│                  └──▶ [PostgreSQL / SQLite]                    │    │
│                                                                 │    │
│  [FastAPI Server] ──▶ [DatabaseManager]                        │    │
│       │                                                         ◀────┘
│       ▼                                                              │
│  [Streamlit Dashboard]  ──▶ [FastAPI endpoints]                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

*End of System Design — Phase 3 Complete*  
*8 Diagrams delivered: Architecture, DFD (L0+L1), Class, Sequence (2), ER, Use Case, Activity (2), Deployment*
