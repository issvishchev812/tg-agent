import asyncio
from tg_collector import collect_telegram
from telegram_sender import send_news


async def main():
    posts = await collect_telegram()

    for post in posts:
        try:
            send_news(post)
            print(f"Отправлено: {post['source']}")
        except Exception as e:
            print(f"Ошибка отправки: {e}")

    print(f"\nОбработано новостей: {len(posts)}")


if __name__ == "__main__":
    asyncio.run(main())