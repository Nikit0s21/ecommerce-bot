from telegram import ReplyKeyboardMarkup
from app.models import db, User, Visit
from datetime import datetime


async def start_handler(update, context):
    user = update.effective_user
    existing_user = User.query.filter_by(username=user.username).first()

    if not existing_user:
        new_user = User(
            username=user.username,
            email=f"{user.username}@telegram.org",
            password_hash="telegram_auth",
            first_name=user.first_name,
            last_name=user.last_name,
            created_at=datetime.utcnow(),
            is_active=True
        )
        db.session.add(new_user)
        db.session.commit()

    # Логируем визит
    visit = Visit(
        visitor_id=str(user.id),
        user_id=existing_user.id if existing_user else new_user.id,
        page_url="/start",
        created_at=datetime.utcnow()
    )
    db.session.add(visit)
    db.session.commit()

    keyboard = [
        ['/catalog', '/history'],
        ['/help']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n"
        "Я бот интернет-магазина. Вот что я могу:\n\n"
        "🔍 /catalog - Просмотреть каталог товаров\n"
        "📦 /history - История ваших заказов\n"
        "ℹ️ /help - Помощь по использованию бота",
        reply_markup=reply_markup
    )


async def help_handler(update, context):
    await update.message.reply_text(
        "ℹ️ Помощь по использованию бота:\n\n"
        "1. Для поиска товаров просто введите название в чат\n"
        "2. Используйте /catalog для просмотра по категориям\n"
        "3. Нажмите 'Заказать' под товаром для оформления заказа\n"
        "4. Используйте /history для просмотра ваших заказов\n\n"
        "По всем вопросам обращайтесь в поддержку магазина."
    )