import app
import os
import psycopg
from typing import Literal
from app.models import CustomerResponse, CustomerCreate, CustomerOrderResponse
from app.database import fetch_from_db, execute_returning_one
from fastapi import HTTPException, APIRouter

router = APIRouter()


@router.get("/customers", response_model=list[CustomerResponse])
def get_customers():
    query = "SELECT id, name, email, country, created_at FROM customers ORDER BY id"
    result = fetch_from_db(query)
    return result


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customers(customer_id: int):
    query = "SELECT id, name, email, country, created_at FROM customers WHERE id = %s"
    result = fetch_from_db(query, [customer_id], fetch_one=True)
    if result is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return result


@router.get("/customers/{customer_id}/orders", response_model=list[CustomerOrderResponse])
def get_customer_orders(customer_id: int, status: Literal["pending", "shipped", "completed", "cancelled"] | None = None):
    query = "SELECT * from customers where id = %s"
    customer = execute_returning_one(query, [customer_id])
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    
    query = """
        SELECT o.id as order_id, o.order_date, o.status as status,
        coalesce(sum(oi.quantity * oi.unit_price), 0) as total_price
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.customer_id = %s
    """
    params = [customer_id]

    if status is not None:
        query += " AND o.status = %s"
        params.append(status)

    query += " GROUP BY o.id ORDER BY o.order_date DESC, o.id DESC"

    result = fetch_from_db(query, params)
    return result



@router.post("/customers", response_model=CustomerResponse, status_code=201)
def create_customer(customer: CustomerCreate):
    query = """
        INSERT INTO customers (name, email, country) VALUES (%s, %s, %s) RETURNING id, name, email, country, created_at
    """
    params = [customer.name, customer.email, customer.country]
    try:
        result = execute_returning_one(query, params)
    except psycopg.errors.UniqueViolation: 
        raise HTTPException(status_code=409, detail="Customer with email already exists")
    return result


def create_table_customers():
    with psycopg.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE customers (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                country TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)


def insert_customers():
    with psycopg.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO customers (name, email, country)
                VALUES
                    ('Anna Andersson', 'anna@example.com', 'Sweden'),
                    ('Erik Svensson', 'erik@example.com', 'Sweden'),
                    ('Maria Johansson', 'maria@example.com', 'Sweden'),
                    ('John Smith', 'john@example.com', 'UK'),
                    ('Emma Wilson', 'emma@example.com', 'UK'),
                    ('Hans Müller', 'hans@example.com', 'Germany'),
                    ('Sophie Weber', 'sophie@example.com', 'Germany'),
                    ('Pierre Dubois', 'pierre@example.com', 'France'),
                    ('Laura Rossi', 'laura@example.com', 'Italy'),
                    ('Peter Hansen', 'peter@example.com', 'Denmark');
            """)
