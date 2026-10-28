from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field

class ProductCreate(BaseModel):
    name: str=Field(min_length=1, description="Product name must not be empty")
    price: float = Field(ge=0, description="Price must be greater than or equal to zero")
    category: str | None = None
    active: bool = True

class ProductResponse(ProductCreate):
    id: int

class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    category: str | None = None
    category: str | None = None
    active: bool = True

class ProductResponse(ProductCreate):
    id: int

class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    category: str | None = None
    active: bool | None = None

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    country: str

class CustomerResponse(CustomerCreate):
    id: int
    created_at: datetime

class OrderResponse(BaseModel):
    order_id: int
    order_date: date
    status: str
    customer_name: str
    total_price: Decimal

class CustomerOrderResponse(BaseModel):
    order_id: int
    order_date: date
    status: str
    total_price: Decimal

class Item(BaseModel):
    product_id: int = Field(gt=0, strict=True, description = "product_id must be greater than 0")
    quantity: int = Field(gt=0, description = "quantity must be greater than 0")

class OrderCreate(BaseModel):
    customer_id: int = Field(gt=0, strict=True, description="customer_id must be greater than 0")
    items: list[Item]=Field(min_length=1, description="the order must have order_items")

class OrderPostResponse(BaseModel):
    id: int
