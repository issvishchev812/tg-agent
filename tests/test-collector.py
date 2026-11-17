import asyncio
from tg_collector import collect_telegram

async def main():
    posts = await collect_telegram()

    for post in posts:
        print("=" * 50)
        print("Источник:", post["source"])
        print("Текст:", post["text"])
        print("Ссылка:", post["url"])


asyncio.run(main())