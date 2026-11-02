import asyncio
from tg_collector import collect_telegram


async def test_llm():
    news = await collect_telegram()

    relevant_count = 0

    for new in news:
        if new["relevant"]:
            relevant_count += 1

            print("\nРезультат:", new)
            print("Релевантность:", new["relevant"])
            print("Выжимка:", new["summary"])
            print("Причина:", new["reason"])
        else:
            print("Нерелевантный текст")

    print(f"\nВсего найдено публикаций: {len(news)}")
    print(f"Релевантных: {relevant_count}")


if __name__ == "__main__":
    asyncio.run(test_llm())