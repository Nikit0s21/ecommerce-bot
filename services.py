from datetime import datetime

import logger
from sqlalchemy.orm import Session
from database import SessionLocal
import models


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def search_products_db(query: str = None, db: Session = next(get_db_session())):
    if query:
        return db.query(models.Product).filter(models.Product.name.ilike(f"%{query}%")).all()
    return db.query(models.Product).all()


def create_order_db(product_id: int, quantity: int, user_id: int, address: str, payment_method: str,
                    db: Session = next(get_db_session())):
    try:
        product = db.query(models.Product).get(product_id)
        if not product:
            raise ValueError("Товар не найден")

        if product.stock < quantity:
            raise ValueError("Недостаточно товара на складе")

        total = product.price * quantity
        order = models.Order(
            user_id=user_id,
            status="pending",
            total=total,
            address=address,
            payment_method=payment_method,
            created_at=datetime.now()
        )

        db.add(order)
        db.flush()  # Частичное сохранение для получения ID

        order_item = models.OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            price=product.price
        )
        db.add(order_item)

        product.stock -= quantity
        db.commit()

        # Возвращаем словарь вместо ORM-объекта
        return {
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "total": order.total,
            "address": order.address,
            "payment_method": order.payment_method,
            "created_at": order.created_at
        }
    except Exception as e:
        db.rollback()
        raise


def get_user_orders_db(user_id: int, db: Session = next(get_db_session())):
    """Получение списка заказов пользователя"""
    try:
        orders = db.query(models.Order).filter(models.Order.user_id == user_id).all()

        # Преобразуем ORM-объекты в словари
        return [
            {
                "id": order.id,
                "status": order.status,
                "total": order.total,
                "address": order.address,
                "payment_method": order.payment_method,
                "created_at": order.created_at
            }
            for order in orders
        ]
    except Exception as e:
        logger.error(f"Error getting orders: {str(e)}")
        raise