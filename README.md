# 🚦 AI-Powered Smart Traffic Management System
An intelligent traffic management system that leverages Computer Vision, Deep Learning, and Artificial Intelligence to monitor real-time traffic using CCTV video streams. The system detects and tracks vehicles, estimates traffic density, dynamically optimizes traffic signal timings, prioritizes emergency vehicles, performs Automatic Number Plate Recognition (ANPR), and provides an interactive analytics dashboard for traffic monitoring.
> **B.Tech Final Year Major Project** — AI + Computer Vision + Deep Learning

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-red.svg)](https://ultralytics.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38-orange.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## 📋 Project Overview

Traditional traffic signals operate on fixed timing regardless of traffic density, causing congestion, fuel wastage, and delayed emergency vehicles. This system replaces fixed-time control with an **AI-powered, real-time adaptive system** that:

| Feature | Description |
|---------|-------------|
| 🔍 **Vehicle Detection** | YOLOv8s detects cars, buses, trucks, motorcycles, bicycles |
| 🎯 **Multi-Object Tracking** | ByteTrack assigns unique IDs to every vehicle |
| 🔢 **Lane Counting** | Virtual counting lines per lane with directional counting |
| 📊 **Density Estimation** | Real-time congestion classification (Low / Medium / High / Very High) |
| 🚦 **Adaptive Signals** | AI algorithm dynamically allocates green-light time by lane density |
| 🚑 **Emergency Priority** | Auto-detects ambulance/fire truck/police → immediate green corridor |
| 🔤 **ANPR** | License plate recognition using EasyOCR + PaddleOCR |
| 📈 **Analytics Dashboard** | Streamlit dashboard with live feed + Plotly interactive charts |
| 🗄️ **Database** | PostgreSQL (production) / SQLite (development) with SQLAlchemy ORM |

---

## 🏗️ Architecture

```
CCTV Input → [YOLOv8 Detector] → [ByteTrack Tracker] → [Vehicle Counter]
                                                               ↓
[Signal Controller] ← [Density Estimator] ← [Lane State]
       ↓
[FastAPI REST API] → [PostgreSQL Database]
       ↓
[Streamlit Dashboard] ← [Plotly Charts]
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Git
- (Optional) NVIDIA GPU with CUDA 11.8+

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd "Smart Traffic Management System"

# Automated setup (creates venv, installs deps, downloads model)
python scripts/setup_env.py
```

### 2. Configure Environment

```bash
# Edit the generated .env file
nano .env  # or open in your editor
```

### 3. Generate Sample Video (for testing)

```bash
source .venv/bin/activate
python scripts/download_sample_video.py
```

### 4. Start the System

```bash
# Terminal 1: Start API server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start dashboard
streamlit run frontend/dashboard.py --server.port 8501
```

### 5. Docker (Alternative)

```bash
docker-compose up --build
# API:       http://localhost:8000
# Dashboard: http://localhost:8501
# API Docs:  http://localhost:8000/docs
```

---

## 📁 Project Structure

```
Smart Traffic Management System/
├── backend/                    # FastAPI application
│   ├── main.py                 # App entry point & lifespan
│   ├── api/
│   │   ├── routes/             # API route handlers
│   │   └── schemas/            # Pydantic request/response models
│   ├── core/                   # Core AI processing modules
│   │   ├── detector.py         # YOLOv8 vehicle detection
│   │   ├── tracker.py          # ByteTrack multi-object tracking
│   │   ├── counter.py          # Lane-based vehicle counting
│   │   ├── density.py          # Traffic density estimation
│   │   ├── signal_controller.py # Adaptive signal algorithm
│   │   ├── emergency.py        # Emergency vehicle detection
│   │   └── anpr.py             # Number plate recognition
│   ├── services/               # Business logic services
│   └── middleware/             # Request logging, CORS, etc.
├── frontend/                   # Streamlit dashboard
│   ├── dashboard.py            # Main dashboard entry point
│   ├── pages/                  # Multi-page dashboard sections
│   └── components/             # Reusable UI components
├── database/                   # Database layer
│   ├── models.py               # SQLAlchemy ORM models
│   ├── crud.py                 # Database operations (CRUD)
│   ├── connection.py           # Database engine & sessions
│   └── migrations/             # Alembic migration scripts
├── config/                     # Configuration management
│   ├── settings.py             # Pydantic BaseSettings
│   └── logging_config.py       # Loguru setup
├── models/
│   └── weights/                # YOLOv8 .pt model files
├── videos/                     # Input video files
├── outputs/                    # Processed frames, plates, reports
├── logs/                       # Application logs
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests (no external deps)
│   └── integration/            # Integration tests (requires DB)
├── scripts/                    # Automation scripts
├── docker/                     # Docker configuration
├── docs/                       # Project documentation (all 16 phases)
├── .env.example                # Environment template
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── pyproject.toml              # Tool configuration (ruff, mypy, pytest)
├── Dockerfile                  # Container build
└── docker-compose.yml          # Multi-service orchestration
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run only unit tests (fast, no DB required)
pytest -m unit

# Run with coverage report
pytest --cov --cov-report=html
open htmlcov/index.html

# Check code quality
ruff check .
mypy .
```

---

## 📊 Performance Targets

| Metric | Target |
|--------|--------|
| Vehicle Detection mAP | ≥ 85% |
| Processing Speed (GPU) | ≥ 20 FPS |
| Processing Speed (CPU) | ≥ 10 FPS |
| ANPR Accuracy | ≥ 80% |
| Emergency Override Latency | ≤ 500ms |
| API Response Time (p95) | ≤ 200ms |
| Test Coverage | ≥ 70% |

---

## 🗄️ Database Schema

| Table | Purpose |
|-------|---------|
| `cameras` | Camera/lane configuration |
| `vehicles` | All detection events |
| `number_plates` | ANPR recognized plates |
| `traffic_records` | Density readings per lane |
| `signal_records` | Signal timing history |
| `emergency_events` | Emergency vehicle events |
| `analytics_hourly` | Aggregated hourly stats |
| `system_config` | Runtime configuration |

---

## 🛣️ SDLC Phases

| Phase | Status | Deliverable |
|-------|--------|-------------|
| 1. Requirement Analysis | ✅ Complete | SRS, Use Cases, Risk Analysis |
| 2. Literature Review | ✅ Complete | 20-citation research review |
| 3. System Design | ✅ Complete | 8 UML/Architecture diagrams |
| 4. Environment Setup | ✅ Complete | Project structure, configs, scripts |
| 5. Database Design | 🔄 In Progress | Schema, models, migrations |
| 6. Backend Development | ⏳ Pending | FastAPI APIs |
| 7–13. Core Modules | ⏳ Pending | Detection, tracking, counting, etc. |
| 14. Dashboard | ⏳ Pending | Streamlit + Plotly |
| 15. Testing | ⏳ Pending | Test suite + evaluation |
| 16. Deployment | ⏳ Pending | Docker + deployment guide |

---

## 📚 Documentation

All documentation is in the `docs/` folder:

- [Requirement Analysis](docs/phase1_requirement_analysis.md)
- [Literature Review](docs/phase2_literature_review.md)
- [System Design](docs/phase3_system_design.md)

---

## 🤝 Tech Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.12+ |
| Detection | YOLOv8 (Ultralytics) + PyTorch |
| Tracking | ByteTrack |
| OCR | EasyOCR + PaddleOCR |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit + Plotly |
| Database | PostgreSQL + SQLite |
| ORM | SQLAlchemy + Alembic |
| Validation | Pydantic v2 |
| Logging | Loguru |
| Testing | pytest + pytest-cov |
| Container | Docker + Docker Compose |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*B.Tech Final Year Project — AI-Powered Smart Traffic Management System*
