"""Konfigurasi global SecureVault."""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "securevault.db"
STEGO_DIR = DATA_DIR / "stego_output"

APP_NAME = "SecureVault"
DONGGLE_FILENAME = "donggle_key.dat"
VAULT_EXT = ".svault"
MAX_FILE_SIZE_MB = 200          # Fernet memproses seluruh file di RAM
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 30

IS_WINDOWS = sys.platform == "win32"

# --- MODE PENGEMBANGAN (hanya untuk testing di luar Windows / tanpa USB) ---
# SECUREVAULT_DONGGLE_DIR : folder biasa dianggap sebagai "flashdisk" (pisahkan dengan ;)
# SECUREVAULT_SKIP_HELLO=1: lewati Windows Hello (JANGAN dipakai saat demo final)
DEV_DONGGLE_DIRS = [p for p in os.environ.get("SECUREVAULT_DONGGLE_DIR", "").split(";") if p]
DEV_SKIP_HELLO = os.environ.get("SECUREVAULT_SKIP_HELLO") == "1"

DATA_DIR.mkdir(exist_ok=True)
STEGO_DIR.mkdir(exist_ok=True)
