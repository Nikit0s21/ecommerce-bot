from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from bot import logger
from database import get_db
import models
import schemas  # Импортируем схемы
from typing import List

app = FastAPI()

@app.get("/products/", response_model=List[schemas.Product])
def search_products(query: str = None, db: Session = Depends(get_db)):
    if query:
        products = db.query(models.Product).filter(models.Product.name.ilike(f"%{query}%")).all()
    else:
        products = db.query(models.Product).all()
    return products


@app.post("/orders/", response_model=schemas.Order)
def create_order(order_data: schemas.OrderCreate, user_id: int, db: Session = Depends(get_db)):
    try:
        # 1. Проверяем существование пользователя
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. Проверяем товар
        product = db.query(models.Product).filter(models.Product.id == order_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.stock < order_data.quantity:
            raise HTTPException(status_code=400, detail="Not enough stock")

        # 3. Создаем заказ
        total = product.price * order_data.quantity
        order = models.Order(
            user_id=user_id,
            status="pending",
            total=total,
            address=order_data.address,
            payment_method=order_data.payment_method,
            created_at=datetime.now()
        )

        db.add(order)
        db.flush()  # Получаем ID заказа без полного коммита

        # 4. Создаем позицию заказа
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=order_data.quantity,
            price=product.price
        )
        db.add(order_item)

        # 5. Обновляем остатки
        product.stock -= order_data.quantity

        # 6. Фиксируем все изменения
        db.commit()

        # 7. Возвращаем заказ, запрашивая его заново
        return db.query(models.Order).filter(models.Order.id == order.id).first()

    except Exception as e:
        db.rollback()
        logger.error(f"Order creation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/orders/", response_model=List[schemas.Order])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()