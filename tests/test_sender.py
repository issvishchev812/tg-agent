from telegram_sender import send_news

send_news({
    "summary": "Тестовая новость — проверка бота",
    "source": "test",
    "reason": "Проверяем доставку сообщений",
    "url": "https://example.com"
})