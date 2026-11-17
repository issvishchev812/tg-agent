import asyncio
from tg_collector import collect_telegram
from telegram_sender import send_news
from state import mark_as_processed, load_state, save_state


async def main():
    posts = await collect_telegram()

    state = load_state()

    for post in posts:
        try:
            print(
                f"НОВОСТЬ: ID={post.get('message_id')}, "
                f"категория={post.get('category')!r}, "
                f"источник={post.get('source')}, "
                f"текст={post.get('summary')}"
            )

            send_news(post)

            mark_as_processed(post["text_hash"])

            channel = post["source"]
            message_id = post["message_id"]

            state[channel] = max(
                state.get(channel, 0),
                message_id
            )
            save_state(state)

            print(f"Отправлено: {channel}")

        except Exception as e:
            print(f"Ошибка отправки: {e}")
            break

    print(f"\nОбработано новостей: {len(posts)}")


if __name__ == "__main__":
    asyncio.run(main())