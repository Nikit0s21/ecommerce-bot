import os
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext import filters
from app.handlers.catalog import catalog_handler, search_handler
from app.handlers.orders import order_handler, order_history_handler
from app.handlers.user import start_handler, help_handler
from config import Config

async def post_init(application):
    # Здесь можно добавить код, который выполнится после инициализации
    await application.bot.set_my_commands([
        ("start", "Запустить бота"),
        ("help", "Помощь"),
        ("catalog", "Просмотр каталога"),
        ("history", "История заказов")
    ])

def main():
    # Создаем Application вместо Updater
    application = Application.builder() \
        .token(Config.TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("catalog", catalog_handler))
    application.add_handler(CommandHandler("history", order_history_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_handler))
    application.add_handler(CallbackQueryHandler(order_handler, pattern='^order_'))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()