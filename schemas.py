from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    category: str | None = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    image_url: str | None = None
    stock: int | None = None
    created_at: datetime | None = None
    rating: float | None = None
    reviews_count: int | None = None
    discount: int | None = None

    class Config:
        from_attributes = True  # Ранее называлось orm_mode=True

class OrderItemBase(BaseModel):
    quantity: int
    price: float

class OrderItemCreate(OrderItemBase):
    product_id: int

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    product: Product

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    status: str
    total: float
    address: str
    payment_method: str

class OrderCreate(BaseModel):
    product_id: int
    quantity: int
    address: str
    payment_method: str

class Order(BaseModel):
    id: int
    user_id: int
    status: str
    total: float
    address: str
    payment_method: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
