from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from services import search_products_db, create_order_db, get_user_orders_db
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "7993583222:AAF9hKB7P-l9VKy7tgsYc2luC2V3KziMStE"

# Состояния бота
STATE_SEARCH = 1
STATE_ORDER = 2


# Обработчик ошибок
async def error_handler(update: object, context: CallbackContext):
    logger.error("Exception while handling an update:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")


# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот магазина. Вот что я могу:\n"
        "/search - Поиск товаров\n"
        "/order - Оформить заказ\n"
        "/history - История заказов"
    )


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите название товара для поиска:")
    context.user_data['state'] = STATE_SEARCH


async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите данные заказа в формате:\n"
        "Артикул Количество Адрес СпособОплаты\n"
        "Например: 123 1 Москва Карта"
    )
    context.user_data['state'] = STATE_ORDER


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = 1
        orders = get_user_orders_db(user_id)

        if not orders:
            await update.message.reply_text("📭 У вас еще нет заказов")
            return

        response = []
        for order in orders:
            order_info = (
                f"🆔 Заказ #{order['id']}\n"
                f"📅 Дата: {order['created_at']}\n"
                f"🔄 Статус: {order['status']}\n"
                f"💳 Сумма: {order['total']} руб.\n"
                f"🏠 Адрес: {order['address']}\n"
                f"💸 Способ оплаты: {order['payment_method']}\n"
                f"────────────────────"
            )
            response.append(order_info)

        # Разбиваем на сообщения по 3 заказа, чтобы не превысить лимит Telegram
        for i in range(0, len(response), 3):
            await update.message.reply_text("\n\n".join(response[i:i + 3]))

    except Exception as e:
        logger.error(f"History error: {str(e)}", exc_info=True)
        await update.message.reply_text("⚠️ Произошла ошибка при получении истории заказов")


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')

    if state == STATE_SEARCH:
        await process_search(update, context)
    elif state == STATE_ORDER:
        await process_order(update, context)
    else:
        await update.message.reply_text("Не понимаю команду. Введите /start для помощи")


async def process_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.message.text
        products = search_products_db(query)

        if not products:
            await update.message.reply_text("Товары не найдены")
            return

        # Формируем читаемый ответ
        response = []
        for product in products:
            product_info = (
                f"🆔 {product.id}\n"
                f"📱 {product.name}\n"
                f"💰 Цена: {product.price} руб.\n"
                f"📦 Остаток: {product.stock} шт."
            )
            if product.description:
                product_info += f"\n📝 {product.description[:100]}..."
            response.append(product_info)

        await update.message.reply_text("\n\n".join(response))
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка при поиске товаров")
    finally:
        context.user_data.pop('state', None)


async def process_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        parts = update.message.text.split()
        if len(parts) < 4:
            raise ValueError("Неверный формат данных. Используйте: Артикул Количество Адрес СпособОплаты")

        user_id = 1

        order_data = {
            "product_id": int(parts[0]),
            "quantity": int(parts[1]),
            "user_id": user_id,
            "address": " ".join(parts[2:-1]),
            "payment_method": parts[-1]
        }

        # Создаем заказ
        order = create_order_db(**order_data)

        await update.message.reply_text(
            f"✅ Заказ #{order['id']} оформлен!\n"
            f"💰 Сумма: {order['total']} руб.\n"
            f"🏠 Адрес: {order['address']}\n"
            f"💳 Способ оплаты: {order['payment_method']}"
        )
    except ValueError as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    except Exception as e:
        logger.error(f"Order error: {str(e)}", exc_info=True)
        await update.message.reply_text("⚠️ Произошла ошибка при оформлении заказа")
    finally:
        context.user_data.pop('state', None)


def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("order", order_command))
    application.add_handler(CommandHandler("history", history_command))

    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Обработчик ошибок
    application.add_error_handler(error_handler)

    application.run_polling()


if __name__ == "__main__":
    main()