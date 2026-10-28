import app
import os
import psycopg
from typing import Literal
from app.models import OrderCreate, OrderResponse, OrderPostResponse, Item
from app.database import fetch_from_db, insert_order_into_db
from fastapi import HTTPException, APIRouter

router = APIRouter()


@router.get("/orders", response_model=list[OrderResponse])
def get_orders(status: Literal["pending", "shipped", "completed", "cancelled"] | None = None):
    params = []
    query = """
        SELECT o.id as order_id, o.customer_id, o.order_date as order_date, o.status as status,
        c.name as customer_name, coalesce(sum(oi.quantity * oi.unit_price), 0) as total_price 
        FROM orders o JOIN customers c ON o.customer_id = c.id 
        LEFT JOIN order_items oi ON o.id = oi.order_id
    """ 
    if status is not None:
        query += " WHERE o.status = %s"
        params.append(status)
    query += " GROUP BY o.id, c.name ORDER BY o.id"
    
    result = fetch_from_db( query, params)

    return result


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    result = fetch_from_db(
        """
            SELECT o.id as order_id, o.customer_id, o.order_date as order_date, o.status as status,
                c.name as customer_name, coalesce(sum(oi.quantity * oi.unit_price), 0) as total_price 
                FROM orders o JOIN customers c ON o.customer_id = c.id 
                LEFT JOIN order_items oi ON o.id = oi.order_id 
                WHERE o.id = %s 
                GROUP BY o.id, c.name
        """, [order_id], fetch_one=True
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


def aggregate_order_items(items: list[Item]) -> dict[int, int]:
    quantities = {}

    for item in items:
        if item.product_id in quantities:
            quantities[item.product_id] += item.quantity
        else:
            quantities[item.product_id] = item.quantity
    return quantities


@router.post("/orders", response_model=OrderPostResponse, status_code=201)
def create_order(order_details: OrderCreate):
    order_items = aggregate_order_items(order_details.items)
    try:
        result = insert_order_into_db(order_details.customer_id, order_items)
    except psycopg.errors.ForeignKeyViolation:
        raise HTTPException(
            status_code=404,
            detail="Customer or product not found"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    return result


def create_table_orders():
    with psycopg.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE orders (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                customer_id BIGINT NOT NULL,
                order_date DATE NOT NULL DEFAULT CURRENT_DATE,
                status TEXT NOT NULL DEFAULT 'pending',

                CONSTRAINT fk_orders_customer
                    FOREIGN KEY (customer_id)
                    REFERENCES customers(id)
                    ON DELETE RESTRICT,

                CONSTRAINT chk_order_status
                    CHECK (status IN ('pending', 'shipped', 'completed', 'cancelled'))
                );
            """)


def insert_orders():
    with psycopg.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
               INSERT INTO orders (customer_id, order_date, status)
                VALUES
                    (1, '2026-09-01', 'completed'),
                    (2, '2026-09-03', 'shipped'),
                    (1, '2026-09-05', 'pending'),
                    (3, '2026-09-07', 'completed'),
                    (4, '2026-09-10', 'shipped'),
                    (5, '2026-09-12', 'pending'),
                    (2, '2026-09-15', 'completed'),
                    (3, '2026-09-18', 'cancelled'),
                    (1, '2026-09-20', 'shipped'),
                    (4, '2026-09-22', 'pending');
            """)


def create_table_order_items():
    with psycopg.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE order_items (
                    order_id BIGINT NOT NULL,
                    product_id BIGINT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price NUMERIC(10,2) NOT NULL,

                    PRIMARY KEY (order_id, product_id),

                    FOREIGN KEY (order_id)
                        REFERENCES orders(id)
                        ON DELETE CASCADE,

                    FOREIGN KEY (product_id)
                        REFERENCES products(id)
                        ON DELETE RESTRICT,

                    CONSTRAINT chk_quantity CHECK (quantity > 0),
                    CONSTRAINT chk_unit_price CHECK (unit_price >= 0)
        );
            """)


def insert_order_items():
    with psycopg.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES
                    (1, 1, 2, 199.00),
                    (1, 2, 1, 349.00),
                    (2, 3, 1, 499.00),
                    (3, 1, 3, 199.00),
                    (3, 4, 2, 129.00),
                    (4, 2, 2, 349.00),
                    (5, 5, 1, 799.00),
                    (5, 1, 1, 199.00),
                    (6, 3, 2, 499.00),
                    (7, 4, 4, 129.00),
                    (7, 5, 1, 799.00),
                    (8, 2, 1, 349.00),
                    (9, 1, 2, 199.00),
                    (9, 3, 1, 499.00);
            """)
