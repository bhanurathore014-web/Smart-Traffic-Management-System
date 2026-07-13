"""
scripts/seed_helpers.py
========================
Helper generators for the seed script.
Produces realistic Indian traffic data without external dependencies.
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone


# ---------------------------------------------------------------------------
# Plate generation
# ---------------------------------------------------------------------------

_STATE_CODES = [
    "MH", "DL", "KA", "TN", "GJ", "RJ", "UP", "WB",
    "AP", "TS", "MP", "PB", "HR", "KL", "BR",
]

_PLATE_SUFFIXES = [
    "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AJ",
    "AK", "AL", "AM", "AN", "AP", "AQ", "AR",
]


def random_plate() -> str:
    """Generate a realistic Indian number plate e.g. MH-12-AB-3456."""
    state = random.choice(_STATE_CODES)
    rto = str(random.randint(1, 99)).zfill(2)
    series = random.choice(_PLATE_SUFFIXES)
    number = str(random.randint(1000, 9999))
    return f"{state}-{rto}-{series}-{number}"


def normalize_plate(plate: str) -> str:
    return plate.upper().replace(" ", "").replace("-", "")


# ---------------------------------------------------------------------------
# Vehicle metadata
# ---------------------------------------------------------------------------

_VEHICLE_TYPES = [
    ("car", 0.45),
    ("motorcycle", 0.25),
    ("truck", 0.10),
    ("bus", 0.08),
    ("auto_rickshaw", 0.08),
    ("bicycle", 0.03),
    ("unknown", 0.01),
]

_COLORS = [
    "white", "silver", "black", "red", "blue",
    "grey", "yellow", "green", "orange", "brown",
]

_MAKES = {
    "car": ["Maruti", "Hyundai", "Tata", "Honda", "Toyota", "Mahindra", "Ford", "Renault"],
    "motorcycle": ["Hero", "Bajaj", "TVS", "Honda", "Royal Enfield", "Yamaha", "Suzuki"],
    "truck": ["Tata", "Ashok Leyland", "Mahindra", "Eicher", "BharatBenz"],
    "bus": ["Tata", "Ashok Leyland", "Volvo", "BEST", "MSRTC"],
    "auto_rickshaw": ["Bajaj", "Piaggio", "Mahindra"],
    "bicycle": ["Hero", "Atlas", "BSA", "Firefox"],
    "unknown": [],
}


def weighted_choice(options: list[tuple[str, float]]) -> str:
    choices, weights = zip(*options)
    return random.choices(choices, weights=weights, k=1)[0]


def random_vehicle_row() -> dict:
    vtype = weighted_choice(_VEHICLE_TYPES)
    makes = _MAKES.get(vtype, [])
    return {
        "id": str(uuid.uuid4()),
        "vehicle_type": vtype,
        "color": random.choice(_COLORS),
        "make": random.choice(makes) if makes else None,
        "model_year": random.randint(2010, 2024) if vtype != "unknown" else None,
        "confidence": round(random.uniform(0.70, 0.99), 3),
    }


# ---------------------------------------------------------------------------
# Camera locations (realistic Indian city grid)
# ---------------------------------------------------------------------------

CAMERA_FIXTURES = [
    {"name": "Andheri East Junction",      "location": "Andheri East, Mumbai",        "latitude": 19.1136, "longitude": 72.8697},
    {"name": "Bandra Kurla Complex Gate",  "location": "BKC, Mumbai",                 "latitude": 19.0652, "longitude": 72.8659},
    {"name": "Powai Lake Crossing",        "location": "Powai, Mumbai",               "latitude": 19.1175, "longitude": 72.9060},
    {"name": "Dadar TT Circle",            "location": "Dadar, Mumbai",               "latitude": 19.0178, "longitude": 72.8478},
    {"name": "Thane Station Road",         "location": "Thane West",                  "latitude": 19.1972, "longitude": 72.9716},
    {"name": "Vashi Sector 10 Signal",     "location": "Vashi, Navi Mumbai",          "latitude": 19.0748, "longitude": 73.0155},
    {"name": "Kurla West Flyover",         "location": "Kurla West, Mumbai",          "latitude": 19.0728, "longitude": 72.8787},
    {"name": "Mulund Check Naka",          "location": "Mulund East, Mumbai",         "latitude": 19.1726, "longitude": 72.9567},
    {"name": "Vikhroli Pipe Road",         "location": "Vikhroli East, Mumbai",       "latitude": 19.1059, "longitude": 72.9307},
    {"name": "Ghatkopar Signal East",      "location": "Ghatkopar East, Mumbai",      "latitude": 19.0866, "longitude": 72.9085},
]


def make_camera_rows() -> list[dict]:
    rows = []
    for cam in CAMERA_FIXTURES:
        rows.append({
            "id": str(uuid.uuid4()),
            "name": cam["name"],
            "location": cam["location"],
            "latitude": cam["latitude"],
            "longitude": cam["longitude"],
            "status": "active",
            "num_lanes": random.choice([2, 3, 4]),
            "stream_url": f"rtsp://camera{len(rows)+1:02d}.traffic.local/stream",
            "ip_address": f"192.168.1.{10 + len(rows)}",
        })
    return rows


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def rush_hour_weight(hour: int) -> float:
    """Higher probability of traffic during peak hours."""
    if 7 <= hour <= 10 or 17 <= hour <= 20:
        return 3.5
    if 11 <= hour <= 16:
        return 1.5
    if 21 <= hour <= 23 or 6 <= hour <= 6:
        return 0.8
    return 0.3   # midnight – 5am


def random_ts_in_hour(base: datetime) -> datetime:
    """Random second within the given hour bucket."""
    offset = random.randint(0, 3599)
    return base + timedelta(seconds=offset)


# ---------------------------------------------------------------------------
# Traffic record row builder
# ---------------------------------------------------------------------------

_DIRECTIONS = ["north", "south", "east", "west"]


def random_traffic_row(
    camera_id: str,
    vehicle_id: str | None,
    plate_id: str | None,
    ts: datetime,
    lane_count: int,
) -> dict:
    speed = None
    if random.random() > 0.1:   # 90% have speed estimate
        speed = round(random.uniform(10, 80), 1)
    return {
        "id": str(uuid.uuid4()),
        "camera_id": camera_id,
        "vehicle_id": vehicle_id,
        "number_plate_id": plate_id,
        "timestamp": ts,
        "direction": random.choice(_DIRECTIONS),
        "lane_number": random.randint(1, max(1, lane_count)),
        "speed_kmh": speed,
        "detection_confidence": round(random.uniform(0.55, 0.99), 3),
        "tracker_id": random.randint(1, 9999),
    }


# ---------------------------------------------------------------------------
# Signal record row builder
# ---------------------------------------------------------------------------

_PHASES = ["red", "green", "yellow", "all_red"]
_PHASE_WEIGHTS = [0.4, 0.45, 0.1, 0.05]
_TRIGGERS = ["adaptive", "fixed", "fixed", "fixed"]   # adaptive is rarer


def random_signal_rows(camera_id: str, start: datetime, count: int) -> list[dict]:
    rows = []
    ts = start
    for _ in range(count):
        phase = random.choices(_PHASES, weights=_PHASE_WEIGHTS, k=1)[0]
        duration = (
            random.uniform(10, 90) if phase == "green"
            else random.uniform(3, 5) if phase == "yellow"
            else random.uniform(10, 60)
        )
        rows.append({
            "id": str(uuid.uuid4()),
            "camera_id": camera_id,
            "timestamp": ts,
            "phase": phase,
            "duration_seconds": round(duration, 1),
            "actual_duration_seconds": round(duration + random.uniform(-2, 2), 1),
            "triggered_by": random.choice(_TRIGGERS),
            "vehicle_count_at_trigger": random.randint(0, 30),
        })
        ts = ts + timedelta(seconds=duration + random.uniform(0, 3))
    return rows


# ---------------------------------------------------------------------------
# Emergency event row builder
# ---------------------------------------------------------------------------

_EMERGENCY_TYPES = ["ambulance", "fire_truck", "police", "vvip"]
_EMERGENCY_WEIGHTS = [0.55, 0.20, 0.20, 0.05]


def random_emergency_row(camera_id: str, vehicle_id: str | None, ts: datetime) -> dict:
    etype = random.choices(_EMERGENCY_TYPES, weights=_EMERGENCY_WEIGHTS, k=1)[0]
    resolved = random.random() < 0.90
    resolved_at = (ts + timedelta(minutes=random.uniform(1, 10))) if resolved else None
    return {
        "id": str(uuid.uuid4()),
        "camera_id": camera_id,
        "vehicle_id": vehicle_id,
        "timestamp": ts,
        "emergency_type": etype,
        "priority": random.randint(1, 3),
        "status": "resolved" if resolved else "active",
        "detection_confidence": round(random.uniform(0.60, 0.99), 3),
        "resolved_at": resolved_at,
        "green_corridor_activated": random.random() < 0.6,
    }


# ---------------------------------------------------------------------------
# System config defaults
# ---------------------------------------------------------------------------

SYSTEM_CONFIG_DEFAULTS = [
    ("signal.min_green_seconds",        "10",   "int",   "Minimum green phase duration"),
    ("signal.max_green_seconds",        "90",   "int",   "Maximum green phase duration"),
    ("signal.yellow_seconds",           "3",    "int",   "Yellow phase duration"),
    ("signal.total_cycle_seconds",      "150",  "int",   "Total signal cycle target"),
    ("density.low_threshold",           "0.25", "float", "Density score below which traffic is 'low'"),
    ("density.medium_threshold",        "0.50", "float", "Density score for 'medium' classification"),
    ("density.high_threshold",          "0.75", "float", "Density score for 'high' classification"),
    ("detection.yolo_conf_threshold",   "0.50", "float", "YOLO minimum confidence to keep a detection"),
    ("anpr.min_confidence",             "0.50", "float", "Minimum OCR confidence to accept a plate"),
    ("emergency.confirm_frames",        "3",    "int",   "Consecutive frames to confirm an emergency vehicle"),
    ("analytics.aggregate_interval_s",  "3600", "int",   "Interval in seconds for hourly aggregation job"),
    ("system.version",                  "1.0.0","string","Deployed system version"),
]


def make_system_config_rows() -> list[dict]:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    return [
        {
            "key": key,
            "value": value,
            "value_type": vtype,
            "description": desc,
            "updated_at": now,
            "updated_by": "seed_script",
        }
        for key, value, vtype, desc in SYSTEM_CONFIG_DEFAULTS
    ]
