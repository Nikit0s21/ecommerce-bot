import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.handlers.catalog import catalog_handler, search_handler
from app.handlers.orders import order_handler, order_history_handler
from app.handlers.user import start_handler, help_handler
from app.models import db, User
from config import Config

def main():
    # Инициализация бота
    updater = Updater(Config.TELEGRAM_TOKEN)
    dp = updater.dispatcher

    # Регистрация обработчиков
    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(CommandHandler("help", help_handler))
    dp.add_handler(CommandHandler("catalog", catalog_handler))
    dp.add_handler(CommandHandler("history", order_history_handler))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), search_handler))
    dp.add_handler(CallbackQueryHandler(order_handler, pattern='^order_'))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()