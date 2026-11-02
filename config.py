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

KEYWORDS = [
    "Роскомнадзор",
    "РКН",
    "реестр запрещённых сайтов",
    "реестр экстремистских материалов",
    "закон о связи",
    "суверенный интернет",
    "интернет-цензура",

    "заблокировал сайт",
    "заблокировали сайт",
    "блокировка сайта",
    "блокировка сервиса",
    "блокировка приложения",
    "блокировка мессенджера",
    "ограничение доступа",
    "ограничили доступ",
    "доступ ограничен",
    "полная блокировка",
    "частичная блокировка",
    "разблокировка",
    "обход блокировки",
    "запрет доступа",

    "замедление интернета",
    "замедление мобильного интернета",
    "замедление трафика",
    "отключение интернета",
    "отключение мобильного интернета",
    "ограничение мобильного интернета",
    "отключение связи",
    "отключение мобильной связи",
    "отключение мобильного трафика",
    "белые списки",

    "блокировка VPN",
    "ограничение VPN",
    "запрет VPN",
    "VPN-сервисы",
    "VPN-протоколы",
    "протокол OpenVPN",
    "WireGuard",
    "VLESS",
    "прокси-сервер",

    "блокировка Telegram",
    "замедление Telegram",
    "блокировка YouTube",
    "замедление YouTube",
    "блокировка Discord",
    "блокировка Instagram",
    "блокировка Facebook",
    "блокировка Twitter",
]

API_KEY = os.getenv("OR_API_KEY")

MODEL = os.getenv("OPENROUTER_MODEL")

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")