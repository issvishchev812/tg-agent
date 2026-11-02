import os
import json
import html
from urllib.request import Request, urlopen

from config import BOT_TOKEN, TARGET_CHAT_ID


def send_news(post):
    if not BOT_TOKEN or not TARGET_CHAT_ID:
        raise ValueError("Не заданы BOT_TOKEN или TARGET_CHAT_ID в .env")

    summary = html.escape(post.get("summary") or post.get("text", "")[:500])
    source = html.escape(post.get("source", "Неизвестный источник"))
    reason = html.escape(post.get("reason", ""))
    url = post.get("url")

    parts = [
        f"<b>{summary}</b>",
        f"Источник: {source}",
    ]

    if reason:
        parts.append(f"<i>{reason}</i>")

    if url:
        parts.append(f'<a href="{html.escape(url, quote=True)}">Открыть оригинал</a>')

    text = "\n\n".join(parts)[:4000]

    payload = {
        "chat_id": TARGET_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    request = Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=15) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result}")

    print("Новость отправлена в канал")