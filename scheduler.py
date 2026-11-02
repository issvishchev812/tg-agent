import asyncio
import time
from run import main

INTERVAL = 600


async def scheduler():
    while True:
        start = time.time()

        print("\n=== Запуск мониторинга ===")

        try:
            await main()
        except Exception as e:
            print(f"Ошибка мониторинга: {e}")

        elapsed = time.time() - start
        sleep_time = max(0, INTERVAL - elapsed)

        print(f"Следующий запуск через {sleep_time:.0f} секунд")
        await asyncio.sleep(sleep_time)


if __name__ == "__main__":
    asyncio.run(scheduler())