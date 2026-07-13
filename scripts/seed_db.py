"""
scripts/seed_db.py
===================
Populate the Smart Traffic Management System database with realistic
historical traffic data to enable immediate dashboard development.

Usage:
    python scripts/seed_db.py                    # 30 days, 10 cameras
    python scripts/seed_db.py --days 7           # 7 days of history
    python scripts/seed_db.py --reset            # drop + recreate tables first
    python scripts/seed_db.py --days 7 --reset   # reset and seed 7 days

Environment:
    DATABASE_URL — must be set (defaults to SQLite dev DB)
"""

from __future__ import annotations

import argparse
import asyncio
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so `database` package is importable
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

from database.session import async_engine, AsyncSessionLocal
from database.base import Base
from scripts.seed_helpers import (
    make_camera_rows,
    make_system_config_rows,
    normalize_plate,
    random_plate,
    random_traffic_row,
    random_vehicle_row,
    random_emergency_row,
    random_signal_rows,
    rush_hour_weight,
    random_ts_in_hour,
)

console = Console()

# ---------------------------------------------------------------------------
# Bulk insert helpers
# ---------------------------------------------------------------------------

BULK_CHUNK = 500   # rows per INSERT batch


async def _bulk_insert(table, rows: list[dict]) -> int:
    """Insert rows in chunks using Core INSERT."""
    total = 0
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for i in range(0, len(rows), BULK_CHUNK):
                chunk = rows[i : i + BULK_CHUNK]
                await session.execute(table.insert(), chunk)
                total += len(chunk)
    return total


# ---------------------------------------------------------------------------
# Seed phases
# ---------------------------------------------------------------------------

async def reset_db() -> None:
    """Drop and recreate all tables."""
    console.print("[bold red]⚠  Resetting database — all data will be lost![/bold red]")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    console.print("[green]✓ Schema recreated[/green]")


async def seed_cameras() -> list[dict]:
    from database.models.camera import Camera
    rows = make_camera_rows()
    await _bulk_insert(Camera.__table__, rows)
    console.print(f"[green]✓ Cameras:[/green] {len(rows)} rows")
    return rows


async def seed_vehicles(n: int = 500) -> list[dict]:
    from database.models.vehicle import Vehicle
    rows = [random_vehicle_row() for _ in range(n)]
    await _bulk_insert(Vehicle.__table__, rows)
    console.print(f"[green]✓ Vehicles:[/green] {len(rows)} rows")
    return rows


async def seed_plates(vehicles: list[dict], n_extra: int = 100) -> list[dict]:
    """Create one plate per vehicle + n_extra re-read plates (lower confidence)."""
    from database.models.number_plate import NumberPlate

    rows = []
    # One plate per vehicle
    for v in vehicles:
        plate = random_plate()
        rows.append({
            "id": str(uuid.uuid4()),
            "vehicle_id": v["id"],
            "plate_text": plate,
            "plate_text_normalized": normalize_plate(plate),
            "region": plate.split("-")[0],
            "confidence": round(random.uniform(0.80, 0.99), 3),
            "ocr_engine": random.choice(["easyocr", "paddleocr"]),
        })
    # Extra re-reads with lower confidence (partial OCR)
    for _ in range(n_extra):
        v = random.choice(vehicles)
        plate = random_plate()
        rows.append({
            "id": str(uuid.uuid4()),
            "vehicle_id": v["id"],
            "plate_text": plate,
            "plate_text_normalized": normalize_plate(plate),
            "region": plate.split("-")[0],
            "confidence": round(random.uniform(0.50, 0.79), 3),
            "ocr_engine": random.choice(["easyocr", "paddleocr"]),
        })
    await _bulk_insert(NumberPlate.__table__, rows)
    console.print(f"[green]✓ Number plates:[/green] {len(rows)} rows")
    return rows


async def seed_traffic_and_signals(
    cameras: list[dict],
    vehicles: list[dict],
    plates: list[dict],
    days: int,
) -> None:
    from database.models.traffic_record import TrafficRecord
    from database.models.signal_record import SignalRecord

    # Pre-index plates by vehicle_id for fast lookup
    plate_by_vehicle: dict[str, str] = {}
    for p in plates:
        if p["vehicle_id"] not in plate_by_vehicle:
            plate_by_vehicle[p["vehicle_id"]] = p["id"]

    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(days=days)

    total_traffic = 0
    total_signals = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total} cameras"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        cam_task = progress.add_task("Seeding traffic & signals", total=len(cameras))

        for cam in cameras:
            cam_id = cam["id"]
            lane_count = cam["num_lanes"]
            traffic_rows: list[dict] = []
            signal_rows: list[dict] = []

            # Iterate hour by hour
            cur = start
            while cur < now:
                hour = cur.hour
                weight = rush_hour_weight(hour)
                count = int(random.gauss(weight * 80, weight * 20))
                count = max(0, min(count, 400))

                for _ in range(count):
                    v = random.choice(vehicles)
                    plate_id = plate_by_vehicle.get(v["id"])
                    ts = random_ts_in_hour(cur)
                    traffic_rows.append(
                        random_traffic_row(cam_id, v["id"], plate_id, ts, lane_count)
                    )

                # ~8 signal cycles per hour
                signal_rows.extend(random_signal_rows(cam_id, cur, count=8))

                cur += timedelta(hours=1)

            inserted_t = await _bulk_insert(TrafficRecord.__table__, traffic_rows)
            inserted_s = await _bulk_insert(SignalRecord.__table__, signal_rows)
            total_traffic += inserted_t
            total_signals += inserted_s
            progress.advance(cam_task)

    console.print(f"[green]✓ Traffic records:[/green] {total_traffic:,} rows")
    console.print(f"[green]✓ Signal records:[/green] {total_signals:,} rows")


async def seed_analytics(cameras: list[dict], days: int) -> None:
    from database.models.analytics_hourly import AnalyticsHourly

    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(days=days)
    rows = []

    for cam in cameras:
        cur = start
        while cur < now:
            hour = cur.hour
            weight = rush_hour_weight(hour)
            count = int(random.gauss(weight * 80, weight * 20))
            count = max(0, count)
            rows.append({
                "id": str(uuid.uuid4()),
                "camera_id": cam["id"],
                "hour_bucket": cur,
                "vehicle_count": count,
                "avg_speed_kmh": round(random.uniform(15, 65), 2),
                "peak_density": round(random.uniform(0.1, 0.95), 3),
                "avg_density": round(random.uniform(0.05, 0.75), 3),
                "car_count": int(count * 0.45),
                "truck_count": int(count * 0.10),
                "motorcycle_count": int(count * 0.25),
                "bus_count": int(count * 0.08),
                "emergency_count": int(count * 0.005),
                "avg_green_duration_s": round(random.uniform(20, 70), 1),
                "signal_cycles": random.randint(4, 12),
                "is_complete": cur < now - timedelta(hours=1),
            })
            cur += timedelta(hours=1)

    from database.models.analytics_hourly import AnalyticsHourly
    await _bulk_insert(AnalyticsHourly.__table__, rows)
    console.print(f"[green]✓ Analytics hourly:[/green] {len(rows):,} rows")


async def seed_emergencies(cameras: list[dict], vehicles: list[dict], n: int = 80) -> None:
    from database.models.emergency_event import EmergencyEvent

    now = datetime.now(timezone.utc)
    rows = []
    for _ in range(n):
        cam = random.choice(cameras)
        v = random.choice(vehicles) if random.random() > 0.2 else None
        days_ago = random.uniform(0, 30)
        ts = now - timedelta(days=days_ago)
        rows.append(random_emergency_row(cam["id"], v["id"] if v else None, ts))

    await _bulk_insert(EmergencyEvent.__table__, rows)
    console.print(f"[green]✓ Emergency events:[/green] {len(rows)} rows")


async def seed_system_config() -> None:
    from database.models.system_config import SystemConfig

    rows = make_system_config_rows()
    # system_config uses key as PK — insert via ORM to handle conflicts
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for row in rows:
                existing = await session.get(SystemConfig, row["key"])
                if existing is None:
                    session.add(SystemConfig(**row))
    console.print(f"[green]✓ System config:[/green] {len(rows)} rows")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def main(days: int, reset: bool) -> None:
    console.rule("[bold cyan]Smart Traffic DB Seeder[/bold cyan]")

    if reset:
        await reset_db()
    else:
        # Ensure tables exist without dropping
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        console.print("[dim]Tables verified (no reset)[/dim]")

    console.print(f"[bold]Seeding {days} day(s) of history across 10 cameras...[/bold]\n")

    cameras = await seed_cameras()
    vehicles = await seed_vehicles(500)
    plates = await seed_plates(vehicles, n_extra=100)
    await seed_traffic_and_signals(cameras, vehicles, plates, days)
    await seed_analytics(cameras, days)
    await seed_emergencies(cameras, vehicles, n=80)
    await seed_system_config()

    await async_engine.dispose()
    console.print("\n[bold green]🎉 Seed complete![/bold green]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed the Smart Traffic Management System database with historical data."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days of historical data to generate (default: 30)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate all tables before seeding",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(days=args.days, reset=args.reset))
