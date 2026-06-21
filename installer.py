# Helper used by main.py to make sure the game's libraries are installed.
# Students don't need to run pip by hand - calling install("name") checks if a
# package can be imported and, if not, downloads it automatically.

import sys
import subprocess
import importlib


def install(package_name):
    """Import `package_name` if present, otherwise pip-install it (binary wheels only)."""
    # Some packages are installed under one name but imported under another.
    # This map tells us what to actually "import" to check if it's present.
    #   - opencv-python      -> import cv2
    #   - pygame-ce          -> import pygame  (community fork, same API)
    package_import_map = {
        "opencv-python": "cv2",
        "pytorch_lightning": "pytorch_lightning",
        "pygame-ce": "pygame",
    }

    # Get the actual import name (falls back to the package name itself)
    import_name = package_import_map.get(package_name, package_name)

    try:
        importlib.import_module(import_name)
        print(f"{package_name} is already installed.")
    except ImportError:
        print(f"{package_name} not found. Installing...")
        try:
            # --only-binary :all: forces pip to use a prebuilt wheel. Without it,
            # if no wheel exists for this Python version, pip tries to COMPILE the
            # package from source - which needs C build tools and usually fails
            # with a confusing error. This way we fail fast with a clear message.
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--only-binary",
                    ":all:",
                    package_name,
                ]
            )
            print(f"{package_name} installed.")
        except subprocess.CalledProcessError:
            print(
                f"\n❌ Could not install '{package_name}'.\n"
                f"   This usually means there is no prebuilt version for your\n"
                f"   Python version ({sys.version_info.major}.{sys.version_info.minor}).\n"
                f"   Tip: this project works best on Python 3.11 or 3.12.\n"
            )
            raise
