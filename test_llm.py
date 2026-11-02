import asyncio

from llm_processor import analyze_text
from tg_collector import collect_telegram


async def test_llm():
    news = await collect_telegram()

    for new in news:

        result = analyze_text(new)

        if result["relevant"]:

            print("Результат:", result)
            print("Релевантность:", result["relevant"])
            print("Выжимка:", result["summary"])
            print("Причина:", result["reason"])
        else:
            print('Нерелевантный текст')

asyncio.run(test_llm())