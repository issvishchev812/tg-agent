import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("PHONE")

CHANNELS = [
    channel.strip()
    for channel in os.getenv("TELEGRAM_CHANNELS", "").split(",")
    if channel.strip()
]