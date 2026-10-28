import psycopg
from psycopg.rows import dict_row
import os


def fetch_from_db(query: str, params: list | None = None, fetch_one: bool = False) -> list[dict] | dict | None:    
    with psycopg.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        row_factory=dict_row
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch_one:
                result = cur.fetchone()
            else:
                result = cur.fetchall()
    return result


def execute_returning_one(query: str, params: list) -> int:
    with psycopg.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        row_factory=dict_row
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
    return result


def insert_order_into_db(customer_id:int, items:dict) -> dict:  
    with psycopg.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        row_factory=dict_row
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO orders (customer_id) VALUES (%s) RETURNING id", [customer_id])
            order_id = cur.fetchone()

            for product_id, quantity in items.items():
                cur.execute("SELECT price FROM products WHERE id = %s", [product_id])
                product = cur.fetchone()
                if product is None:
                    raise ValueError(f"Product {product_id} not found")
                unit_price = product['price']
                cur.execute("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)", (order_id["id"], product_id, quantity, unit_price))

        return order_id
