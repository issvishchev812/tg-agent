import asyncio
import time

from telethon import TelegramClient
from telethon.errors import FloodWaitError

from config import API_ID, API_HASH, CHANNELS, KEYWORDS, BATCH_SIZE
from state import load_state, save_state, get_text_hash, load_processed

from llm_processor import analyze_text

client = TelegramClient("news_session", API_ID, API_HASH)


async def collect_telegram():
    print("1. Начинаем сбор...", flush=True)

    posts = []
    state = load_state()

    wait_until = state.get("_flood_wait_until", 0)
    if time.time() < wait_until:
        remaining = int(wait_until - time.time())
        print(
            f"Telegram на паузе. Осталось ждать {remaining} секунд.",
            flush=True
        )
        return []

    processed = load_processed()
    seen = set()

    print("2. Загружено состояние:", state, flush=True)

    try:
        await client.start()

    except FloodWaitError as e:
        state["_flood_wait_until"] = time.time() + e.seconds
        save_state(state)

        print(
            f"Ограничение при подключении. Ждём {e.seconds} секунд.",
            flush=True
        )
        return []

    print("3. Подключились к Telegram!", flush=True)

    batch_index = state.get("_batch_index", 0)
    start = batch_index * BATCH_SIZE
    batch = CHANNELS[start:start + BATCH_SIZE]

    flood_waited = False
    channel_index = state.get("_channel_index", 0)

    for channel_offset, channel in enumerate(batch[channel_index:], start=channel_index):
        print(f"4. Обрабатываем канал: {channel}", flush=True)

        try:
            await asyncio.sleep(8)

            entity = await client.get_input_entity(channel)

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

                    print(
                        f"РЕЗУЛЬТАТ LLM: канал={channel}, "
                        f"ID={message.id}, "
                        f"relevant={analysis.get('relevant')}, "
                        f"category={analysis.get('category')!r}, "
                        f"summary={analysis.get('summary')!r}",
                        flush=True
                    )

                    if not isinstance(analysis, dict) or "relevant" not in analysis:
                        raise ValueError("Некорректный ответ LLM")

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

                username = channel.lstrip("@") if isinstance(channel, str) else None

                url = (
                    f"https://t.me/{username}/{message.id}"
                    if username else None
                )

                posts.append({
                    "source": channel,
                    "source_type": "telegram",
                    "external_id": str(message.id),
                    "message_id": message.id,
                    "text": message.message,
                    "url": url,
                    "published_at": message.date.isoformat(),
                    "text_hash": text_hash,
                    "relevant": analysis["relevant"],
                    "summary": analysis.get("summary", ""),
                    "category": analysis.get("category", ""),
                    "reason": analysis.get("reason", "")
                })

            if last_processed_id > last_id:
                state[channel] = last_processed_id

                print(
                    f"Новый ID для {channel}: {last_processed_id}",
                    flush=True
                )

                save_state(state)

            channel_index = channel_offset + 1
            state["_channel_index"] = channel_index
            save_state(state)


        except FloodWaitError as e:
            flood_waited = True
            state["_flood_wait_until"] = time.time() + e.seconds
            print(
                f"Telegram ограничил запросы. Нужно подождать {e.seconds} секунд. "
                "Останавливаем сбор до следующего запуска.",
                flush=True
            )
            break


        except Exception as e:
            print(f"Ошибка канала {channel}: {e}", flush=True)
            channel_index = channel_offset + 1
            state["_channel_index"] = channel_index
            save_state(state)
            continue

    save_state(state)

    total_batches = (len(CHANNELS) + BATCH_SIZE - 1) // BATCH_SIZE

    if not flood_waited:
        batch_index = (batch_index + 1) % total_batches
        state["_channel_index"] = 0
    else:
        state["_channel_index"] = channel_index

    if not flood_waited:
        state.pop("_flood_wait_until", None)

    state["_batch_index"] = batch_index
    save_state(state)

    print(
        f"Состояние сохранено. Группа: {batch_index + 1}, "
        f"следующий канал: {state['_channel_index'] + 1}",
        flush=True
    )

    return posts
