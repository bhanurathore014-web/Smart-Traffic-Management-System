"""
alembic/versions/0001_initial_schema.py
=========================================
Initial schema — creates all 8 tables for the Smart Traffic Management System.

Revision ID: 0001
Revises: (none — first migration)
Create Date: 2026-07-13
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # cameras
    # -----------------------------------------------------------------------
    op.create_table(
        "cameras",
        sa.Column("id", sa.String(36), primary_key=True, comment="UUID v4 primary key"),
        sa.Column("name", sa.String(120), nullable=False, comment="Human-readable camera name"),
        sa.Column("location", sa.String(255), nullable=False, comment="Street / intersection description"),
        sa.Column("latitude", sa.Float, nullable=False, comment="Decimal degrees latitude"),
        sa.Column("longitude", sa.Float, nullable=False, comment="Decimal degrees longitude"),
        sa.Column("stream_url", sa.String(512), nullable=True, comment="RTSP / HLS stream URL"),
        sa.Column("ip_address", sa.String(45), nullable=True, comment="Camera IP (IPv4 or IPv6)"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active", comment="Operational status enum"),
        sa.Column("num_lanes", sa.Integer, nullable=False, server_default="4", comment="Number of monitored lanes"),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_camera_lat"),
        sa.CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_camera_lng"),
        comment="CCTV camera device registry",
    )
    op.create_index("ix_cameras_status", "cameras", ["status"])
    op.create_index("ix_cameras_location", "cameras", ["location"])

    # -----------------------------------------------------------------------
    # vehicles
    # -----------------------------------------------------------------------
    op.create_table(
        "vehicles",
        sa.Column("id", sa.String(36), primary_key=True, comment="UUID v4 primary key"),
        sa.Column("vehicle_type", sa.String(30), nullable=False, server_default="unknown", comment="YOLO-classified vehicle type"),
        sa.Column("color", sa.String(30), nullable=True, comment="Dominant body color"),
        sa.Column("make", sa.String(60), nullable=True, comment="Manufacturer brand"),
        sa.Column("model_year", sa.Integer, nullable=True, comment="Estimated model year"),
        sa.Column("confidence", sa.Float, nullable=True, comment="Detection confidence score 0-1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        comment="Deduplicated catalogue of observed vehicles",
    )
    op.create_index("ix_vehicles_type", "vehicles", ["vehicle_type"])

    # -----------------------------------------------------------------------
    # number_plates
    # -----------------------------------------------------------------------
    op.create_table(
        "number_plates",
        sa.Column("id", sa.String(36), primary_key=True, comment="UUID v4 primary key"),
        sa.Column("vehicle_id", sa.String(36), sa.ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("plate_text", sa.String(20), nullable=False, comment="Raw OCR plate string"),
        sa.Column("plate_text_normalized", sa.String(20), nullable=True, comment="Uppercase stripped for matching"),
        sa.Column("region", sa.String(60), nullable=True, comment="State / RTO region code"),
        sa.Column("confidence", sa.Float, nullable=False, server_default="0.0", comment="OCR confidence 0-1"),
        sa.Column("ocr_engine", sa.String(20), nullable=True, comment="easyocr | paddleocr"),
        sa.Column("crop_image_path", sa.String(512), nullable=True, comment="Path to saved plate crop image"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("confidence >= 0.0 AND confidence <= 1.0", name="ck_plate_confidence"),
        comment="OCR-extracted number plate reads",
    )
    op.create_index("ix_number_plates_plate_text", "number_plates", ["plate_text"])
    op.create_index("ix_number_plates_vehicle_id", "number_plates", ["vehicle_id"])

    # -----------------------------------------------------------------------
    # traffic_records
    # -----------------------------------------------------------------------
    op.create_table(
        "traffic_records",
        sa.Column("id", sa.String(36), primary_key=True, comment="UUID v4 primary key"),
        sa.Column("camera_id", sa.String(36), sa.ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False),
        sa.Column("vehicle_id", sa.String(36), sa.ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("number_plate_id", sa.String(36), sa.ForeignKey("number_plates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment="Event time (UTC)"),
        sa.Column("direction", sa.String(10), nullable=False, server_default="unknown", comment="Travel direction enum"),
        sa.Column("lane_number", sa.Integer, nullable=False, server_default="1", comment="Lane index 1-N"),
        sa.Column("speed_kmh", sa.Float, nullable=True, comment="Estimated speed km/h"),
        sa.Column("detection_confidence", sa.Float, nullable=True, comment="YOLO confidence 0-1"),
        sa.Column("bbox_x1", sa.Integer, nullable=True),
        sa.Column("bbox_y1", sa.Integer, nullable=True),
        sa.Column("bbox_x2", sa.Integer, nullable=True),
        sa.Column("bbox_y2", sa.Integer, nullable=True),
        sa.Column("tracker_id", sa.Integer, nullable=True, comment="ByteTrack track ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("speed_kmh >= 0", name="ck_traffic_speed_positive"),
        sa.CheckConstraint("lane_number >= 1", name="ck_traffic_lane_min"),
        sa.CheckConstraint("detection_confidence >= 0.0 AND detection_confidence <= 1.0", name="ck_traffic_conf"),
        comment="Vehicle detection crossing events — high-volume append-mostly table",
    )
    op.create_index("ix_traffic_camera_timestamp", "traffic_records", ["camera_id", "timestamp"])
    op.create_index("ix_traffic_timestamp", "traffic_records", ["timestamp"])
    op.create_index("ix_traffic_vehicle_id", "traffic_records", ["vehicle_id"])

    # -----------------------------------------------------------------------
    # signal_records
    # -----------------------------------------------------------------------
    op.create_table(
        "signal_records",
        sa.Column("id", sa.String(36), primary_key=True, comment="UUID v4 primary key"),
        sa.Column("camera_id", sa.String(36), sa.ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment="Phase-start timestamp (UTC)"),
        sa.Column("phase", sa.String(20), nullable=False, comment="Signal colour / phase enum"),
        sa.Column("duration_seconds", sa.Float, nullable=False, server_default="0.0", comment="Planned duration in seconds"),
        sa.Column("actual_duration_seconds", sa.Float, nullable=True, comment="Actual duration after phase ends"),
        sa.Column("triggered_by", sa.String(20), nullable=False, server_default="fixed", comment="What caused this phase change"),
        sa.Column("lane_id", sa.Integer, nullable=True, comment="Specific lane (null = intersection-wide)"),
        sa.Column("vehicle_count_at_trigger", sa.Integer, nullable=True, comment="Queue length that triggered adaptive change"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("duration_seconds >= 0", name="ck_signal_duration_positive"),
        comment="Signal phase change log — one row per phase transition",
    )
    op.create_index("ix_signal_camera_timestamp", "signal_records", ["camera_id", "timestamp"])
    op.create_index("ix_signal_timestamp", "signal_records", ["timestamp"])

    # -----------------------------------------------------------------------
    # emergency_events
    # -----------------------------------------------------------------------
    op.create_table(
        "emergency_events",
        sa.Column("id", sa.String(36), primary_key=True, comment="UUID v4 primary key"),
        sa.Column("camera_id", sa.String(36), sa.ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False),
        sa.Column("vehicle_id", sa.String(36), sa.ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, comment="Detection time (UTC)"),
        sa.Column("emergency_type", sa.String(20), nullable=False, server_default="unknown", comment="Type of emergency vehicle"),
        sa.Column("priority", sa.Integer, nullable=False, server_default="1", comment="Override priority 1-5"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active", comment="Resolution status"),
        sa.Column("detection_confidence", sa.Float, nullable=True, comment="YOLO confidence 0-1"),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True, comment="Timestamp when event resolved"),
        sa.Column("green_corridor_activated", sa.Boolean, nullable=False, server_default="false", comment="Green corridor triggered"),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("priority >= 1 AND priority <= 5", name="ck_emergency_priority_range"),
        sa.CheckConstraint("detection_confidence >= 0.0 AND detection_confidence <= 1.0", name="ck_emergency_conf"),
        comment="Emergency vehicle detection events and signal override log",
    )
    op.create_index("ix_emergency_camera_timestamp", "emergency_events", ["camera_id", "timestamp"])
    op.create_index("ix_emergency_status", "emergency_events", ["status"])

    # -----------------------------------------------------------------------
    # analytics_hourly
    # -----------------------------------------------------------------------
    op.create_table(
        "analytics_hourly",
        sa.Column("id", sa.String(36), primary_key=True, comment="UUID v4 primary key"),
        sa.Column("camera_id", sa.String(36), sa.ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hour_bucket", sa.DateTime(timezone=True), nullable=False, comment="Hour start timestamp (UTC)"),
        sa.Column("vehicle_count", sa.Integer, nullable=False, server_default="0", comment="Total vehicles in this hour"),
        sa.Column("avg_speed_kmh", sa.Float, nullable=True, comment="Mean speed km/h"),
        sa.Column("peak_density", sa.Float, nullable=True, comment="Maximum density score 0-1"),
        sa.Column("avg_density", sa.Float, nullable=True, comment="Mean density score 0-1"),
        sa.Column("car_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("truck_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("motorcycle_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("bus_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("emergency_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("avg_green_duration_s", sa.Float, nullable=True, comment="Mean green phase duration"),
        sa.Column("signal_cycles", sa.Integer, nullable=False, server_default="0", comment="Full signal cycles"),
        sa.Column("is_complete", sa.Boolean, nullable=False, server_default="false", comment="True once hour has fully elapsed"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("camera_id", "hour_bucket", name="uq_analytics_camera_hour"),
        sa.CheckConstraint("vehicle_count >= 0", name="ck_analytics_count_positive"),
        sa.CheckConstraint("avg_speed_kmh >= 0", name="ck_analytics_speed_positive"),
        sa.CheckConstraint("peak_density >= 0.0 AND peak_density <= 1.0", name="ck_analytics_density_range"),
        comment="Pre-aggregated hourly metrics for dashboard charts",
    )
    op.create_index("ix_analytics_camera_hour", "analytics_hourly", ["camera_id", "hour_bucket"])
    op.create_index("ix_analytics_hour_bucket", "analytics_hourly", ["hour_bucket"])

    # -----------------------------------------------------------------------
    # system_config
    # -----------------------------------------------------------------------
    op.create_table(
        "system_config",
        sa.Column("key", sa.String(120), primary_key=True, comment="Unique config key"),
        sa.Column("value", sa.Text, nullable=False, comment="String-serialised value"),
        sa.Column("value_type", sa.String(20), nullable=False, server_default="string", comment="Type hint"),
        sa.Column("description", sa.Text, nullable=True, comment="Human-readable description"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_by", sa.String(80), nullable=True, comment="Operator / system that last changed this"),
        comment="Runtime-tunable operational configuration",
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("system_config")
    op.drop_table("analytics_hourly")
    op.drop_table("emergency_events")
    op.drop_table("signal_records")
    op.drop_table("traffic_records")
    op.drop_table("number_plates")
    op.drop_table("vehicles")
    op.drop_table("cameras")
