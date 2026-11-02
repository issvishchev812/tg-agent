import asyncio

from telethon import TelegramClient

from config import API_ID, API_HASH, CHANNELS, KEYWORDS
from state import load_state, save_state, get_text_hash, load_processed, mark_as_processed

from llm_processor import analyze_text

client = TelegramClient("news_session", API_ID, API_HASH)


async def collect_telegram():
    print("1. Начинаем сбор...", flush=True)

    posts = []
    state = load_state()

    processed = load_processed()
    seen = set()

    print("2. Загружено состояние:", state, flush=True)

    await client.start()

    print("3. Подключились к Telegram!", flush=True)

    for channel in CHANNELS:
        print(f"4. Обрабатываем канал: {channel}", flush=True)

        try:
            entity = await client.get_entity(channel)

            last_id = state.get(channel, 0)

            print(f"Последний сохранённый ID: {last_id}", flush=True)

            messages = list(reversed(await asyncio.wait_for(
                client.get_messages(entity, limit=5),
                timeout=30
            )))

            last_processed_id = last_id

            for message in messages:

                if not message.message:
                    last_processed_id = message.id
                    continue

                text = message.message.lower()

                if not any(keyword.lower() in text for keyword in KEYWORDS):
                    last_processed_id = message.id
                    continue

                text_hash = get_text_hash(text)

                if text_hash in processed or text_hash in seen:
                    last_processed_id = message.id
                    continue

                try:
                    analysis = analyze_text(text)

                    if not isinstance(analysis, dict) or "relevant" not in analysis:
                        raise ValueError("Некорректный ответ LLM")

                    mark_as_processed(text_hash)

                except Exception as e:
                    print(
                        f"Ошибка анализа новости {channel}, ID {message.id}: {e}",
                        flush=True
                    )
                    break

                seen.add(text_hash)
                last_processed_id = message.id

                if not analysis["relevant"]:
                    print(f"Нерелевантная новость: {channel}, ID {message.id}")
                    continue

                username = getattr(entity, "username", None)

                url = (
                    f"https://t.me/{username}/{message.id}"
                    if username else None
                )

                posts.append({
                    "source": channel,
                    "source_type": "telegram",
                    "external_id": str(message.id),
                    "text": message.message,
                    "url": url,
                    "published_at": message.date.isoformat(),
                    "text_hash": text_hash,
                    "relevant": analysis["relevant"],
                    "summary": analysis.get("summary", ""),
                    "reason": analysis.get("reason", "")
                })

            if last_processed_id > last_id:
                state[channel] = last_processed_id

                print(
                    f"Новый ID для {channel}: {last_processed_id}",
                    flush=True
                )

        except Exception as e:
            print(f"Ошибка канала {channel}: {e}", flush=True)
            continue

    save_state(state)

    print("7. Состояние сохранено:", state, flush=True)
    print(f"Всего публикаций: {len(posts)}", flush=True)

    return posts
