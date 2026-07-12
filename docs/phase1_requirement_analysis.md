# Software Requirements Specification (SRS)
# AI-Powered Smart Traffic Management System

**Document Version:** 1.0  
**Date:** 2026-07-12  
**Project Title:** AI-Powered Smart Traffic Management System using Computer Vision and Deep Learning  
**Prepared By:** [Your Name], B.Tech Final Year Project  
**Institution:** [Your Institution]  
**Guide:** [Supervisor Name]

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Problem Statement](#2-problem-statement)
3. [Objectives](#3-objectives)
4. [Scope](#4-scope)
5. [Stakeholders](#5-stakeholders)
6. [Functional Requirements](#6-functional-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [System Constraints](#8-system-constraints)
9. [Feasibility Study](#9-feasibility-study)
10. [Assumptions and Dependencies](#10-assumptions-and-dependencies)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the functional and non-functional requirements for the **AI-Powered Smart Traffic Management System**. The system leverages Computer Vision and Deep Learning to replace traditional fixed-time traffic signal controls with an intelligent, real-time adaptive system.

This document serves as the baseline contract between all project stakeholders and forms the foundation for all subsequent design and implementation phases.

### 1.2 Document Conventions

| Term | Definition |
|------|-----------|
| SRS  | Software Requirements Specification |
| FR   | Functional Requirement |
| NFR  | Non-Functional Requirement |
| ANPR | Automatic Number Plate Recognition |
| YOLOv8 | You Only Look Once v8 — real-time object detection model |
| ByteTrack | Multi-object tracking algorithm using byte-level association |
| FPS  | Frames Per Second |
| mAP  | Mean Average Precision |
| OCR  | Optical Character Recognition |

### 1.3 Intended Audience

- **Project Supervisor / Evaluators** — to review system goals and scope
- **Developers (You)** — as a blueprint for implementation
- **Traffic Department / End Users** — to understand system capabilities
- **System Administrators** — for deployment and maintenance planning

### 1.4 Project References

| Reference | Source |
|-----------|--------|
| YOLOv8 Paper | Ultralytics, 2023 |
| ByteTrack Paper | Zhang et al., 2022 — *ByteTrack: Multi-Object Tracking by Associating Every Detection Box* |
| DeepSORT Paper | Wojke et al., 2017 |
| COCO Dataset | Lin et al., 2014 |
| BDD100K Dataset | Yu et al., 2020 |
| CCPD Dataset | Xu et al., 2018 |
| Webster's Signal Timing Method | Webster, 1958 |
| Adaptive Signal Control Theory | FHWA, USA |

---

## 2. Problem Statement

### 2.1 Current Traffic Signal Limitations

Traditional traffic management systems operate on **fixed pre-programmed timers**, allocating equal green-light duration to all lanes regardless of actual traffic conditions. This static approach creates the following critical problems:

#### 2.1.1 Congestion and Inefficiency
- Fixed timers do not respond to real-time traffic density fluctuations.
- Lanes with low vehicle counts receive the same green time as high-density lanes.
- Peak-hour traffic causes severe bottlenecks that fixed timers cannot mitigate.
- Average urban commuters lose **50–100 hours per year** to traffic congestion (INRIX 2023 Report).

#### 2.1.2 Environmental Impact
- Vehicles idling at unnecessarily long red lights emit excess CO₂, NOx, and particulate matter.
- Fuel wastage at intersections contributes to **30% of total urban fuel consumption** (EPA estimates).

#### 2.1.3 Emergency Vehicle Delays
- Ambulances, fire trucks, and police vehicles face the same red-light delays as ordinary vehicles.
- Studies show that a 1-minute delay in ambulance response time increases patient mortality risk by **10%** (NHTSA, 2022).
- Current systems have no mechanism to automatically detect and prioritize emergency vehicles.

#### 2.1.4 Lack of Traffic Data
- Fixed-timer systems collect zero real-time traffic data.
- Traffic planning agencies lack granular data to make informed infrastructure decisions.
- No historical pattern analysis is possible without sensor-based or vision-based systems.

#### 2.1.5 No Vehicle Identification
- Hit-and-run vehicles, stolen vehicles, and traffic violators cannot be automatically identified.
- Manual ANPR systems are expensive and not integrated with signal control.

### 2.2 Quantified Impact (India-Specific Context)

| Metric | Value |
|--------|-------|
| Annual economic loss due to traffic congestion (India) | ₹1.5 Lakh Crore (~$18 Billion) |
| CO₂ emission from urban traffic | 330 million tonnes/year |
| Emergency vehicle delays at intersections | 45 seconds average per intersection |
| Road accident deaths per year (India) | 1.68 Lakh (2022, MoRTH) |

---

## 3. Objectives

### 3.1 Primary Objectives

| ID | Objective |
|----|----------|
| OBJ-01 | Detect vehicles in real-time from CCTV video streams using YOLOv8 with ≥85% mAP |
| OBJ-02 | Track individual vehicles across frames using unique IDs via ByteTrack |
| OBJ-03 | Count vehicles per lane with directional counting (entering/exiting) |
| OBJ-04 | Estimate traffic density levels (Low / Medium / High / Very High) per lane |
| OBJ-05 | Dynamically calculate and assign optimal green-light durations using an AI algorithm |
| OBJ-06 | Detect emergency vehicles and trigger automatic signal override with green corridor |
| OBJ-07 | Perform Automatic Number Plate Recognition (ANPR) using OCR (EasyOCR / PaddleOCR) |
| OBJ-08 | Store all traffic events, vehicle detections, signal timings, and plates in PostgreSQL |
| OBJ-09 | Display real-time and historical analytics via an interactive Streamlit dashboard |
| OBJ-10 | Achieve minimum 20 FPS processing speed on GPU and ≥10 FPS on CPU fallback |

### 3.2 Secondary Objectives

| ID | Objective |
|----|----------|
| OBJ-11 | Generate configurable traffic reports (hourly, daily, weekly) |
| OBJ-12 | Support multiple simultaneous camera feeds (minimum 4 lanes) |
| OBJ-13 | Provide a RESTful API backend for system integration |
| OBJ-14 | Containerize the entire system using Docker for portability |
| OBJ-15 | Design the system to be extensible (siren detection, GPS integration as future modules) |

---

## 4. Scope

### 4.1 In Scope

- **Input:** CCTV video files (MP4/AVI) and simulated RTSP live streams
- **Detection:** Cars, buses, trucks, motorcycles, bicycles, ambulances, fire trucks, police vehicles
- **Tracking:** ByteTrack multi-object tracking with unique vehicle IDs
- **Counting:** Per-lane vehicle counts (4 lanes supported by default, configurable)
- **Density:** Real-time congestion classification using vehicle count + occupancy + speed
- **Signal Control:** AI-optimized dynamic green-light timing with min/max constraints
- **ANPR:** License plate detection and OCR for recognized vehicles
- **Database:** PostgreSQL for production; SQLite for development
- **Dashboard:** Streamlit web application with Plotly charts
- **API:** FastAPI RESTful endpoints for all system modules
- **Deployment:** Docker containerization; deployment on local/Render/Railway

### 4.2 Out of Scope (Future Enhancements)

- Real-time RTSP hardware camera integration (simulated in this version)
- Acoustic siren detection via microphones
- Live GPS tracking of emergency vehicles
- Traffic violation penalty system (red-light jumping detection)
- Integration with traffic control hardware (physical signal boxes)
- Mobile application

---

## 5. Stakeholders

| Stakeholder | Role | Interest |
|-------------|------|----------|
| Municipal Traffic Department | Primary User | Reduce congestion, improve flow |
| Police Department | Secondary User | Emergency vehicle priority, ANPR lookup |
| City Planners | Analyst | Infrastructure decision data |
| Hospital Emergency Teams | Beneficiary | Faster ambulance routes |
| General Public | End Beneficiary | Reduced travel time, less pollution |
| Project Developer | Builder | Deliver a working production system |
| Project Supervisor | Evaluator | Academic and technical validation |

---

## 6. Functional Requirements

### 6.1 Module 1 — Vehicle Detection

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | The system SHALL detect vehicles in each video frame using YOLOv8 | Critical |
| FR-02 | Detection SHALL include: Car, Bus, Truck, Motorcycle, Bicycle, Ambulance, Fire Truck, Police Vehicle | Critical |
| FR-03 | Each detection SHALL output: bounding box (x, y, w, h), vehicle class, confidence score | Critical |
| FR-04 | Confidence threshold SHALL be configurable (default: 0.5) | High |
| FR-05 | The system SHALL filter detections by a configurable Region of Interest (ROI) per lane | High |
| FR-06 | Detection SHALL run at ≥20 FPS on GPU hardware | High |

### 6.2 Module 2 — Multi-Object Tracking

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-07 | The system SHALL assign a unique Track ID to every detected vehicle | Critical |
| FR-08 | Track IDs SHALL persist across frames as long as the vehicle is visible | Critical |
| FR-09 | The system SHALL handle occlusions by re-associating lost tracks (max 30 frames) | High |
| FR-10 | Tracking SHALL use ByteTrack as the primary algorithm | Critical |
| FR-11 | Vehicle trajectory history SHALL be maintained per track ID | Medium |

### 6.3 Module 3 — Vehicle Counting

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-12 | The system SHALL maintain a separate vehicle count for each lane (1–4) | Critical |
| FR-13 | Counting SHALL use a virtual counting line; vehicles crossing it are counted | Critical |
| FR-14 | The system SHALL count vehicles entering and exiting each lane separately | High |
| FR-15 | Counts SHALL be persistent and reset at configurable intervals (e.g., hourly) | Medium |
| FR-16 | Per-class counts SHALL be available (how many cars, buses, etc., per lane) | High |

### 6.4 Module 4 — Traffic Density Estimation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-17 | The system SHALL compute traffic density for each lane every processing cycle | Critical |
| FR-18 | Density SHALL factor in: vehicle count, lane occupancy ratio, estimated speed | High |
| FR-19 | Density SHALL be classified as: Low (<20%), Medium (20–50%), High (50–80%), Very High (>80%) | Critical |
| FR-20 | Density scores SHALL be time-averaged over a configurable window (default: 5 seconds) | High |

### 6.5 Module 5 — Adaptive Traffic Signal Optimization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-21 | The system SHALL compute dynamic green-light durations based on density per lane | Critical |
| FR-22 | Minimum green time SHALL be configurable (default: 10 seconds) | Critical |
| FR-23 | Maximum green time SHALL be configurable (default: 90 seconds) | Critical |
| FR-24 | Total cycle time SHALL be bounded (default: 120–180 seconds) | High |
| FR-25 | No lane SHALL be starved for more than one full cycle | Critical |
| FR-26 | Signal state transitions SHALL be logged with timestamps | High |
| FR-27 | Yellow/transition times SHALL be included in the cycle calculation | Medium |

### 6.6 Module 6 — Emergency Vehicle Detection

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-28 | The system SHALL detect ambulances, fire trucks, and police vehicles | Critical |
| FR-29 | On emergency vehicle detection, the system SHALL immediately override the current signal cycle | Critical |
| FR-30 | The lane containing the emergency vehicle SHALL receive a green light | Critical |
| FR-31 | All other lanes SHALL be set to red during the emergency override | Critical |
| FR-32 | After the emergency vehicle passes (leaves the ROI), the system SHALL resume the normal cycle | Critical |
| FR-33 | Emergency events SHALL be logged with: timestamp, vehicle type, lane, duration | High |
| FR-34 | Emergency alerts SHALL be displayed on the dashboard in real-time | High |

### 6.7 Module 7 — ANPR (Automatic Number Plate Recognition)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-35 | The system SHALL detect license plate regions within detected vehicle bounding boxes | Critical |
| FR-36 | Detected plate regions SHALL be cropped and passed to an OCR engine | Critical |
| FR-37 | OCR SHALL be performed using EasyOCR (primary) with PaddleOCR as fallback | High |
| FR-38 | Recognized plate text SHALL be stored with vehicle ID, timestamp, confidence score | Critical |
| FR-39 | Plate recognition accuracy SHALL target ≥80% for standard Indian plates | High |
| FR-40 | Unreadable plates SHALL be flagged (low confidence) and stored as images for manual review | Medium |

### 6.8 Module 8 — Analytics Dashboard

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-41 | The dashboard SHALL display a live processed video feed | Critical |
| FR-42 | Real-time vehicle counts per lane SHALL be displayed | Critical |
| FR-43 | Current traffic density per lane SHALL be displayed with color indicators | Critical |
| FR-44 | Current signal status (GREEN / YELLOW / RED + remaining time) SHALL be shown | Critical |
| FR-45 | Emergency alerts SHALL appear with visual and textual notifications | Critical |
| FR-46 | Vehicle class distribution chart (pie/bar) SHALL be available | High |
| FR-47 | Hourly and daily traffic trend charts SHALL be displayed | High |
| FR-48 | Peak hour analysis SHALL be available | Medium |
| FR-49 | Recognized number plate logs SHALL be searchable | High |
| FR-50 | Signal timing history chart SHALL be displayed | Medium |

### 6.9 Module 9 — Database Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-51 | All vehicle detection events SHALL be stored with full metadata | Critical |
| FR-52 | Traffic density readings SHALL be logged per lane per timestamp | Critical |
| FR-53 | All signal state changes SHALL be stored | Critical |
| FR-54 | Emergency events SHALL have a dedicated table with all relevant fields | Critical |
| FR-55 | Recognized number plates SHALL be stored with images (optional) | High |
| FR-56 | The system SHALL support database migrations using Alembic | High |

### 6.10 Module 10 — Logging and Monitoring

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-57 | All system events SHALL be logged using Loguru with configurable log levels | High |
| FR-58 | Log rotation SHALL be configured (daily rotation, 30-day retention) | Medium |
| FR-59 | System errors SHALL be logged with full stack traces | Critical |
| FR-60 | Processing FPS and latency metrics SHALL be logged every 10 seconds | Medium |

---

## 7. Non-Functional Requirements

### 7.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | Real-time detection processing speed | ≥20 FPS (GPU), ≥10 FPS (CPU) |
| NFR-02 | Vehicle detection mAP | ≥85% on validation set |
| NFR-03 | ANPR recognition accuracy | ≥80% for clear plate images |
| NFR-04 | API response time (non-video) | <200ms for 95th percentile |
| NFR-05 | Dashboard load time | <3 seconds initial load |
| NFR-06 | Emergency override latency | <500ms from detection to signal change |

### 7.2 Reliability

| ID | Requirement |
|----|-------------|
| NFR-07 | The system SHALL handle corrupted/incomplete video frames gracefully |
| NFR-08 | Database transactions SHALL be ACID-compliant |
| NFR-09 | The system SHALL auto-recover from brief video stream disconnections |
| NFR-10 | The signal algorithm SHALL always ensure at least one lane has green |

### 7.3 Scalability

| ID | Requirement |
|----|-------------|
| NFR-11 | The system architecture SHALL support adding more than 4 lanes with configuration changes only |
| NFR-12 | The database design SHALL efficiently handle >1 million records without redesign |
| NFR-13 | The API SHALL support horizontal scaling via Docker Compose |

### 7.4 Usability

| ID | Requirement |
|----|-------------|
| NFR-14 | The dashboard SHALL be operable without technical expertise |
| NFR-15 | All charts SHALL be interactive (zoom, hover, filter) |
| NFR-16 | Color-blind accessible color schemes SHALL be used |

### 7.5 Security

| ID | Requirement |
|----|-------------|
| NFR-17 | Sensitive configurations (DB passwords, API keys) SHALL use environment variables |
| NFR-18 | API endpoints SHALL validate all inputs via Pydantic schemas |
| NFR-19 | Database credentials SHALL NOT be hardcoded in source code |

### 7.6 Maintainability

| ID | Requirement |
|----|-------------|
| NFR-20 | All Python code SHALL follow PEP 8 style guidelines |
| NFR-21 | All public functions/classes SHALL have docstrings |
| NFR-22 | Type hints SHALL be used throughout the codebase |
| NFR-23 | Code coverage of unit tests SHALL be ≥70% |

### 7.7 Portability

| ID | Requirement |
|----|-------------|
| NFR-24 | The system SHALL run on Linux, macOS, and Windows via Docker |
| NFR-25 | The system SHALL support NVIDIA CUDA GPU and CPU-only mode |
| NFR-26 | All dependencies SHALL be pinned in requirements.txt |

---

## 8. System Constraints

| Constraint | Description |
|------------|-------------|
| Hardware | Minimum: 8GB RAM, 4-core CPU. Recommended: NVIDIA GPU with ≥4GB VRAM |
| Software | Python 3.12+, CUDA 11.8+ (optional), Docker 24+ |
| Data | System uses pre-recorded video files; live RTSP is a future enhancement |
| Dataset | YOLOv8 uses pretrained COCO weights; fine-tuning is optional |
| Time | Project timeline: 16 phases over one academic semester |
| Budget | Open-source tools only; no paid APIs or services required |

---

## 9. Feasibility Study

### 9.1 Technical Feasibility

| Component | Feasibility | Justification |
|-----------|------------|---------------|
| YOLOv8 Detection | ✅ HIGH | Ultralytics provides pretrained models; COCO includes all required vehicle classes |
| ByteTrack | ✅ HIGH | Open-source Python implementation available; proven in real-world deployments |
| ANPR with EasyOCR | ✅ HIGH | EasyOCR supports multi-language OCR; works well on standard number plate formats |
| FastAPI Backend | ✅ HIGH | Mature, well-documented framework; excellent async support |
| Streamlit Dashboard | ✅ HIGH | Purpose-built for ML/AI data apps; rapid development |
| PostgreSQL DB | ✅ HIGH | Industry-standard; extensive Python ORM support via SQLAlchemy |
| Docker Deployment | ✅ HIGH | Standard containerization; widely supported |

### 9.2 Operational Feasibility

The system can be operated by non-technical traffic management staff via the Streamlit dashboard. The interface requires no programming knowledge. System administration (deployment, updates) requires basic Docker knowledge.

### 9.3 Economic Feasibility

| Category | Cost |
|----------|------|
| Software licenses | ₹0 (all open-source) |
| Cloud deployment (Railway/Render free tier) | ₹0 |
| GPU compute (Google Colab for fine-tuning) | ₹0 |
| Development hardware | Existing personal computer |
| **Total Project Cost** | **₹0** |

For real deployment:
| Category | Estimate |
|----------|----------|
| Server with GPU (AWS g4dn.xlarge) | ~₹25,000/month |
| CCTV cameras (4 units) | ~₹40,000 one-time |

### 9.4 Schedule Feasibility

The project is divided into 16 phases, achievable within a 16-week academic semester at approximately 1 phase per week.

---

## 10. Assumptions and Dependencies

### 10.1 Assumptions

1. Input video quality is sufficient for vehicle detection (minimum 480p resolution).
2. Vehicles are filmed from a bird's-eye/overhead camera angle (standard CCTV placement).
3. Number plates follow standard Indian format (e.g., MH04AB1234).
4. The system processes one intersection at a time in this version.
5. The development machine has Python 3.12 and internet access for package downloads.

### 10.2 Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.12+ | Core runtime |
| ultralytics | ≥8.3.0 | YOLOv8 detection |
| opencv-python | ≥4.10.0 | Video processing |
| fastapi | ≥0.115.0 | Backend API |
| streamlit | ≥1.38.0 | Dashboard |
| sqlalchemy | ≥2.0.0 | ORM |
| alembic | ≥1.13.0 | DB migrations |
| easyocr | ≥1.7.2 | Number plate OCR |
| loguru | ≥0.7.0 | Structured logging |
| pydantic | ≥2.9.0 | Data validation |
| plotly | ≥5.24.0 | Interactive charts |
| torch | ≥2.4.0 | Deep learning backend |
| numpy | ≥1.26.0 | Numerical ops |
| pandas | ≥2.2.0 | Data analysis |

---

*End of SRS — Phase 1 Deliverable 1 of 3*
