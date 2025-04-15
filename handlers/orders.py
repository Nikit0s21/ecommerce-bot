from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.models import db, Order, OrderItem, Product, User
from datetime import datetime


def order_handler(update, context):
    query = update.callback_query
    product_id = int(query.data.split('_')[1])

    product = Product.query.get(product_id)
    if not product:
        query.answer("Товар не найден")
        return

    user = User.query.filter_by(username=query.from_user.username).first()
    if not user:
        query.answer("Сначала зарегистрируйтесь с помощью /start")
        return

    # Создаем новый заказ
    new_order = Order(
        user_id=user.id,
        created_at=datetime.utcnow(),
        status="pending",
        total=product.price,
        address=user.address or "Не указан",
        payment_method="online"
    )
    db.session.add(new_order)
    db.session.commit()

    # Добавляем товар в заказ
    order_item = OrderItem(
        order_id=new_order.id,
        product_id=product.id,
        quantity=1,
        price=product.price
    )
    db.session.add(order_item)
    db.session.commit()

    query.answer("Заказ оформлен!")
    query.edit_message_text(f"✅ Заказ #{new_order.id} оформлен!\n"
                            f"Товар: {product.name}\n"
                            f"Сумма: {product.price} ₽\n"
                            f"Статус: {new_order.status}")


def order_history_handler(update, context):
    user = User.query.filter_by(username=update.effective_user.username).first()
    if not user:
        update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
        return

    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).limit(10).all()

    if not orders:
        update.message.reply_text("У вас пока нет заказов")
        return

    for order in orders:
        items = OrderItem.query.filter_by(order_id=order.id).all()
        items_text = "\n".join(
            f"{item.product.name} - {item.quantity} x {item.price} ₽"
            for item in items
        )

        message = (
            f"📦 Заказ #{order.id}\n"
            f"📅 Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"💰 Сумма: {order.total} ₽\n"
            f"🚚 Статус: {order.status}\n"
            f"\nТовары:\n{items_text}"
        )

        update.message.reply_text(message)