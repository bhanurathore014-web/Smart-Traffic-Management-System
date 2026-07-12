#!/usr/bin/env python3
"""
Environment Setup Script
=========================
Automates the complete development environment setup:
  1. Creates and activates a Python virtual environment
  2. Installs all dependencies
  3. Copies .env.example → .env
  4. Downloads YOLOv8 model weights
  5. Initialises the database
  6. Verifies GPU availability

Run: python scripts/setup_env.py
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# ANSI colors for pretty output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

PROJECT_ROOT = Path(__file__).parent.parent
VENV_DIR = PROJECT_ROOT / ".venv"


def header(text: str) -> None:
    """Print a styled section header."""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}  {text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}")


def success(text: str) -> None:
    print(f"{GREEN}  ✔  {text}{RESET}")


def warn(text: str) -> None:
    print(f"{YELLOW}  ⚠  {text}{RESET}")


def error(text: str) -> None:
    print(f"{RED}  ✘  {text}{RESET}")


def info(text: str) -> None:
    print(f"     {text}")


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    return subprocess.run(cmd, check=True, **kwargs)


def check_python_version() -> None:
    """Ensure Python 3.12+ is being used."""
    header("Checking Python Version")
    version = sys.version_info
    info(f"Python {version.major}.{version.minor}.{version.micro}")
    if version < (3, 12):
        error(f"Python 3.12+ required. Current: {version.major}.{version.minor}")
        sys.exit(1)
    success("Python version OK")


def create_virtual_environment() -> None:
    """Create a Python virtual environment."""
    header("Creating Virtual Environment")
    if VENV_DIR.exists():
        warn(f"Virtual environment already exists at {VENV_DIR}")
        return
    run([sys.executable, "-m", "venv", str(VENV_DIR)])
    success(f"Virtual environment created at {VENV_DIR}")


def get_python_executable() -> Path:
    """Get the Python executable inside the virtual environment."""
    if platform.system() == "Windows":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def install_dependencies() -> None:
    """Install production + development dependencies."""
    header("Installing Dependencies")
    python = get_python_executable()

    info("Upgrading pip...")
    run([str(python), "-m", "pip", "install", "--upgrade", "pip"])

    info("Installing production requirements...")
    run([str(python), "-m", "pip", "install", "-r", str(PROJECT_ROOT / "requirements.txt")])

    info("Installing development requirements...")
    run([str(python), "-m", "pip", "install", "-r", str(PROJECT_ROOT / "requirements-dev.txt")])

    success("All dependencies installed")


def setup_environment_file() -> None:
    """Copy .env.example to .env if it doesn't exist."""
    header("Setting Up Environment File")
    env_example = PROJECT_ROOT / ".env.example"
    env_file = PROJECT_ROOT / ".env"

    if env_file.exists():
        warn(".env already exists — skipping copy")
        info("Review .env to ensure all values are correct")
        return

    shutil.copy(env_example, env_file)
    success(".env created from .env.example")
    warn("IMPORTANT: Edit .env and set your DATABASE_URL and other secrets!")


def download_yolo_model() -> None:
    """Download YOLOv8s model weights."""
    header("Downloading YOLOv8 Model Weights")
    weights_dir = PROJECT_ROOT / "models" / "weights"
    weights_dir.mkdir(parents=True, exist_ok=True)
    model_path = weights_dir / "yolov8s.pt"

    if model_path.exists():
        warn("YOLOv8s weights already exist — skipping download")
        return

    python = get_python_executable()
    script = (
        "from ultralytics import YOLO; "
        f"model = YOLO('yolov8s.pt'); "
        f"import shutil; "
        f"shutil.move('yolov8s.pt', '{model_path}')"
    )

    info("Downloading YOLOv8s from Ultralytics (this may take a moment)...")
    try:
        run([str(python), "-c", script], cwd=str(PROJECT_ROOT))
        success(f"YOLOv8s weights saved to {model_path}")
    except subprocess.CalledProcessError:
        # Ultralytics auto-downloads to ~/.ultralytics; that's fine too
        warn("Could not move model file. Ultralytics will auto-download on first run.")


def initialize_database() -> None:
    """Run Alembic migrations to initialize the database."""
    header("Initializing Database")
    python = get_python_executable()
    db_dir = PROJECT_ROOT / "database"
    db_dir.mkdir(parents=True, exist_ok=True)

    info("Running Alembic migrations...")
    try:
        run(
            [str(python), "-m", "alembic", "upgrade", "head"],
            cwd=str(PROJECT_ROOT),
        )
        success("Database initialized successfully")
    except subprocess.CalledProcessError:
        warn("Alembic not yet configured — skipping DB init (will be set up in Phase 5)")


def check_gpu() -> None:
    """Check CUDA/MPS GPU availability."""
    header("Checking GPU Availability")
    python = get_python_executable()
    script = (
        "import torch; "
        "cuda = torch.cuda.is_available(); "
        "mps = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available(); "
        "print(f'CUDA: {cuda}'); "
        "print(f'MPS (Apple): {mps}'); "
        "print(f'Device: {torch.cuda.get_device_name(0) if cuda else \"CPU only\"}')"
    )
    try:
        result = run([str(python), "-c", script], capture_output=True, text=True)
        for line in result.stdout.strip().split("\n"):
            info(line)
        if "True" in result.stdout:
            success("GPU acceleration available!")
        else:
            warn("No GPU detected — running in CPU mode (expect lower FPS)")
    except Exception:
        warn("Could not check GPU — torch may not be installed yet")


def print_next_steps() -> None:
    """Print instructions for next steps."""
    header("Setup Complete!")

    if platform.system() == "Windows":
        activate_cmd = r".venv\Scripts\activate"
    else:
        activate_cmd = "source .venv/bin/activate"

    print(f"""
{GREEN}{BOLD}Environment setup complete. Next steps:

  1. Activate virtual environment:
     {activate_cmd}

  2. Edit your .env file:
     nano .env  (or open in your editor)

  3. Start the API server:
     uvicorn backend.main:app --reload --port 8000

  4. Start the dashboard (new terminal):
     streamlit run frontend/dashboard.py

  5. Run tests:
     pytest

  6. Check code quality:
     ruff check .
     mypy .

{RESET}""")


def main() -> None:
    """Run complete environment setup."""
    print(f"\n{BOLD}Smart Traffic Management System — Environment Setup{RESET}")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Project Root: {PROJECT_ROOT}")

    check_python_version()
    create_virtual_environment()
    install_dependencies()
    setup_environment_file()
    download_yolo_model()
    initialize_database()
    check_gpu()
    print_next_steps()


if __name__ == "__main__":
    main()
