from telethon import TelegramClient
from config import API_ID, API_HASH, TABLE_NAME
from excel_parser import get_chat_names


client = TelegramClient("chat-analyzer", API_ID, API_HASH)


async def collect_telegram():
    posts = []

    # Получаем ссылки на чаты из Excel
    chat_links = get_chat_names(TABLE_NAME)

    await client.start()

    try:
        for chat_link in chat_links:
            try:
                entity = await client.get_entity(chat_link)

                username = getattr(entity, "username", None)
                chat_title = getattr(entity, "title", chat_link)

                async for message in client.iter_messages(entity, limit=10):
                    if not message.message:
                        continue

                    # Ссылка на сообщение
                    if username:
                        url = f"https://t.me/{username}/{message.id}"
                    elif hasattr(entity, "megagroup") or hasattr(entity, "broadcast"):
                        url = f"https://t.me/c/{entity.id}/{message.id}"
                    else:
                        url = None

                    posts.append({
                        "source": chat_title,
                        "source_type": "telegram_chat",
                        "external_id": str(message.id),
                        "chat_id": str(entity.id),
                        "text": message.message,
                        "url": url,
                        "published_at": message.date.isoformat(),
                    })

                print(f"Обработан чат: {chat_title}")

            except Exception as e:
                print(f"Ошибка чата {chat_link}: {e}")

    finally:
        await client.disconnect()

    return posts
