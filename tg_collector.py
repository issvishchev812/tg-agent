import asyncio

from telethon import TelegramClient

from config import API_ID, API_HASH, CHANNELS
from state import load_state, save_state


client = TelegramClient("news_session", API_ID, API_HASH)


async def collect_telegram():
    print("1. Начинаем сбор...", flush=True)

    posts = []
    state = load_state()

    print("2. Загружено состояние:", state, flush=True)

    await client.start()

    print("3. Подключились к Telegram!", flush=True)

    for channel in CHANNELS:
        print(f"4. Обрабатываем канал: {channel}", flush=True)

        try:
            entity = await client.get_entity(channel)

            last_id = state.get(channel, 0)

            print(f"Последний сохранённый ID: {last_id}", flush=True)

            messages = await asyncio.wait_for(
                client.get_messages(
                    entity,
                    limit=20,
                    min_id=last_id
                ),
                timeout=30
            )

            max_id = last_id

            for message in reversed(messages):

                # Запоминаем ID даже у публикаций без текста
                max_id = max(max_id, message.id)

                if not message.message:
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
                    "published_at": message.date.isoformat()
                })

            # Обновляем состояние канала
            if max_id > last_id:
                state[channel] = max_id

                print(
                    f"Новый ID для {channel}: {max_id}",
                    flush=True
                )

        except Exception as e:
            print(f"Ошибка канала {channel}: {e}", flush=True)

    # Сохраняем состояние всех каналов
    save_state(state)

    print("7. Состояние сохранено:", state, flush=True)
    print(f"Всего публикаций: {len(posts)}", flush=True)

    return posts