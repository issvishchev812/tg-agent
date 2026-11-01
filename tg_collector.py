from telethon import TelegramClient
from config import API_ID, API_HASH, CHANNELS

client = TelegramClient("news_session", API_ID, API_HASH)

async def collect_telegram():
    posts = []

    await client.start()

    for channel in CHANNELS:
        try:
            entity = await client.get_entity(channel)
            username = getattr(entity, "username", None)

            async for message in client.iter_messages(entity, limit=10):
                if not message.message:
                    continue

                url = f"https://t.me/{username}/{message.id}" if username else None

                posts.append({
                    "source": channel,
                    "source_type": "telegram",
                    "external_id": str(message.id),
                    "text": message.message,
                    "url": url,
                    "published_at": message.date.isoformat(),
                })

        except Exception as e:
            print(f"Ошибка канала {channel}: {e}")

    await client.disconnect()
    return posts