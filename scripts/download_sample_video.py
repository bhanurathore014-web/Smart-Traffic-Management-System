#!/usr/bin/env python3
"""
Download Sample Traffic Video
==============================
Downloads a public domain traffic video for testing and development.
Uses the UA-DETRAC dataset sample or falls back to a synthetic generator.
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

VIDEOS_DIR = Path(__file__).parent.parent / "videos"

# Public domain traffic video (Pexels / Pixabay CC0)
SAMPLE_VIDEO_URL = (
    "https://www.pexels.com/download/video/2053855/"
    "?h=720&w=1280"
)

# Fallback: OpenCV-based synthetic traffic video generator
def generate_synthetic_video(output_path: Path, num_frames: int = 300) -> None:
    """
    Generate a synthetic traffic video for testing when no real video is available.

    Creates a video with moving colored rectangles simulating vehicles
    on a 4-lane road. Useful for unit testing and CI/CD pipelines.

    Args:
        output_path: Path to save the generated video.
        num_frames: Number of frames to generate (default: 300 = 10s at 30fps).
    """
    import random
    import cv2
    import numpy as np

    width, height = 1280, 720
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    # Simulate 4 lanes
    lane_width = width // 4
    vehicle_colors = {
        "car": (200, 200, 200),
        "bus": (100, 200, 100),
        "truck": (150, 100, 50),
        "motorcycle": (200, 100, 200),
    }

    # Initialize vehicles
    vehicles = []
    for lane in range(4):
        for _ in range(random.randint(2, 5)):
            vehicles.append({
                "lane": lane,
                "x": lane * lane_width + random.randint(10, lane_width - 60),
                "y": random.randint(-100, height),
                "w": random.randint(40, 80),
                "h": random.randint(60, 120),
                "speed": random.randint(2, 8),
                "color": random.choice(list(vehicle_colors.values())),
            })

    for _ in range(num_frames):
        frame = np.ones((height, width, 3), dtype=np.uint8) * 50  # Dark gray road

        # Draw lane markings
        for lane in range(1, 4):
            x = lane * lane_width
            for y in range(0, height, 40):
                cv2.line(frame, (x, y), (x, y + 20), (255, 255, 0), 2)

        # Draw counting line
        counting_y = int(height * 0.6)
        cv2.line(frame, (0, counting_y), (width, counting_y), (0, 255, 0), 2)
        cv2.putText(frame, "COUNTING LINE", (10, counting_y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Move and draw vehicles
        for v in vehicles:
            v["y"] += v["speed"]
            if v["y"] > height + 50:
                v["y"] = -v["h"]
                v["x"] = v["lane"] * lane_width + random.randint(10, lane_width - 60)
            cv2.rectangle(
                frame,
                (v["x"], v["y"]),
                (v["x"] + v["w"], v["y"] + v["h"]),
                v["color"],
                -1,
            )
            # Windshield
            cv2.rectangle(
                frame,
                (v["x"] + 5, v["y"] + 5),
                (v["x"] + v["w"] - 5, v["y"] + 20),
                (150, 230, 255),
                -1,
            )

        writer.write(frame)

    writer.release()
    print(f"Synthetic video saved to: {output_path}")
    print(f"  Frames: {num_frames} | FPS: {fps} | Duration: {num_frames/fps:.1f}s")


def main() -> None:
    """Download or generate sample traffic video."""
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIDEOS_DIR / "sample_traffic.mp4"

    if output_path.exists():
        print(f"Sample video already exists: {output_path}")
        return

    print("Generating synthetic traffic video for testing...")
    try:
        generate_synthetic_video(output_path, num_frames=600)
        print("✔ Synthetic video created successfully.")
        print("\nFor real traffic footage, download from:")
        print("  - UA-DETRAC: https://detrac-db.rit.albany.edu/")
        print("  - Pexels (free): https://www.pexels.com/search/videos/traffic/")
        print("  - VIRAT: http://www.viratdata.org/")
    except ImportError:
        print("OpenCV not installed yet. Run setup_env.py first.")
        sys.exit(1)


if __name__ == "__main__":
    main()
