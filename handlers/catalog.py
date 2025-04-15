from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.models import Product, db


def catalog_handler(update, context):
    categories = db.session.query(Product.category).distinct().all()
    keyboard = [
        [InlineKeyboardButton(category[0], callback_data=f"category_{category[0]}")]
        for category in categories
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите категорию:', reply_markup=reply_markup)


def search_handler(update, context):
    query = update.message.text
    products = Product.query.filter(Product.name.ilike(f"%{query}%")).limit(10).all()

    if not products:
        update.message.reply_text("Товары не найдены")
        return

    for product in products:
        keyboard = [[InlineKeyboardButton("Заказать", callback_data=f"order_{product.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = (
            f"🏷 {product.name}\n"
            f"💰 Цена: {product.price} ₽\n"
            f"📦 В наличии: {product.stock} шт.\n"
            f"⭐ Рейтинг: {product.rating}/5\n"
            f"\n{product.description}"
        )

        if product.image_url:
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=product.image_url,
                caption=message,
                reply_markup=reply_markup
            )
        else:
            update.message.reply_text(message, reply_markup=reply_markup)