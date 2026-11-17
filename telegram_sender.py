import os
import json
import html
from urllib.request import Request, urlopen

from config import BOT_TOKEN, NEWS_CHAT, VPN_CHAT


def send_news(post):
    if not BOT_TOKEN or not NEWS_CHAT or not VPN_CHAT:
        raise ValueError("Не заданы BOT_TOKEN или NEWS_CHAT или VPN_CHAT в .env")

    summary = html.escape(post.get("summary") or post.get("text", "")[:500])
    source = html.escape(post.get("source", "Неизвестный источник"))
    category = html.escape(post.get("category", ""))
    reason = html.escape(post.get("reason", ""))
    url = post.get("url")

    category = post.get("category", "").strip()

    if category == "news":
        target_chat_id = NEWS_CHAT
    elif category == "service_outage":
        target_chat_id = VPN_CHAT
    else:
        raise ValueError(f"Неизвестная категория: {category!r}")

    parts = [
        f"<b>{summary}</b>",
        f"Источник: {source}",
    ]

    if reason:
        parts.append(f"<i>{reason}</i>")

    if reason:
        parts.append(f"<i>{category}</i>")

    if url:
        parts.append(f'<a href="{html.escape(url, quote=True)}">Открыть оригинал</a>')

    text = "\n\n".join(parts)[:4000]

    payload = {
        "chat_id": target_chat_id,
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