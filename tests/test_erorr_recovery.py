
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import tg_collector


async def test_error_recovery():
    channel = "test_channel"

    # Подменяем состояние, чтобы не затрагивать рабочие файлы
    fake_state = {channel: 100}
    fake_processed = set()

    messages = [
        MagicMock(
            id=101,
            message="Роскомнадзор заблокировал новый сервис",
            date=MagicMock(isoformat=lambda: "2026-11-02T10:00:00+00:00")
        ),
        MagicMock(
            id=102,
            message="Роскомнадзор ограничил доступ к сайту",
            date=MagicMock(isoformat=lambda: "2026-11-02T11:00:00+00:00")
        ),
    ]

    for message in messages:
        message.message = message.message

    # Первый запуск: LLM падает на первой новости
    with (
        patch.object(tg_collector, "CHANNELS", [channel]),
        patch.object(tg_collector, "KEYWORDS", ["Роскомнадзор"]),
        patch.object(tg_collector, "load_state", return_value=fake_state.copy()),
        patch.object(tg_collector, "load_processed", return_value=fake_processed.copy()),
        patch.object(tg_collector, "save_state") as save_state,
        patch.object(tg_collector, "mark_as_processed"),
        patch.object(tg_collector, "get_text_hash", side_effect=lambda x: x),
        patch.object(tg_collector, "analyze_text", side_effect=Exception("Тестовая ошибка LLM")),
        patch.object(tg_collector.client, "start", new_callable=AsyncMock),
        patch.object(tg_collector.client, "get_entity", new_callable=AsyncMock,
                     return_value=MagicMock(username="test")),
        patch.object(tg_collector.client, "get_messages", new_callable=AsyncMock,
                     return_value=messages),
    ):
        await tg_collector.collect_telegram()

        saved_state = save_state.call_args.args[0]

        assert saved_state[channel] == 100, (
            f"ОШИБКА: ID обновился до {saved_state[channel]}"
        )

    print("Первый тест пройден: ID проблемной новости не сохранён.")

    # Второй запуск: LLM работает
    with (
        patch.object(tg_collector, "CHANNELS", [channel]),
        patch.object(tg_collector, "KEYWORDS", ["Роскомнадзор"]),
        patch.object(tg_collector, "load_state", return_value=fake_state.copy()),
        patch.object(tg_collector, "load_processed", return_value=fake_processed.copy()),
        patch.object(tg_collector, "save_state") as save_state,
        patch.object(tg_collector, "mark_as_processed"),
        patch.object(tg_collector, "get_text_hash", side_effect=lambda x: x),
        patch.object(tg_collector, "analyze_text", return_value={
            "relevant": True,
            "summary": "Тестовая новость",
            "reason": "Тест"
        }),
        patch.object(tg_collector.client, "start", new_callable=AsyncMock),
        patch.object(tg_collector.client, "get_entity", new_callable=AsyncMock,
                     return_value=MagicMock(username="test")),
        patch.object(tg_collector.client, "get_messages", new_callable=AsyncMock,
                     return_value=messages),
    ):
        await tg_collector.collect_telegram()

        saved_state = save_state.call_args.args[0]

        assert saved_state[channel] == 102, (
            f"ОШИБКА: ожидался ID 102, получен {saved_state[channel]}"
        )

    print("Второй тест пройден: после восстановления новости обработаны.")
    print("\nПроверка восстановления после ошибки LLM пройдена!")


if __name__ == "__main__":
    asyncio.run(test_error_recovery())
