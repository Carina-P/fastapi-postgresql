import os
import psycopg
from app.models import ProductResponse, ProductCreate, ProductUpdate
from app.database import fetch_from_db, execute_returning_one
from fastapi import HTTPException, APIRouter

router = APIRouter()

@router.get("/products", response_model=list[ProductResponse])
def get_products(active: bool | None = None, min_price: float | None = None, max_price: float | None = None, category: str | None = None):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price cannot be greater than max_price")
    terms = []
    params = []
    if active is not None:
        terms.append("active = %s")
        params.append(active)
    if min_price is not None:
        terms.append("price >= %s")
        params.append(min_price)
    if max_price is not None:
        terms.append("price <= %s")
        params.append(max_price)
    if category is not None:
        terms.append("category = %s")
        params.append(category)
        
    query = "SELECT id, name, price, category, active FROM products"
    if terms:
        query += " WHERE " + " AND ".join(terms)
    query += " ORDER BY id"
    result = fetch_from_db(query, params)
    return result


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    result = fetch_from_db(
        "SELECT id, name, price, category, active FROM products WHERE id = %s", [product_id], 
        fetch_one=True
        )
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return result    


@router.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate):
    product_dict = product.model_dump(exclude_unset=True)
    query = "UPDATE products SET "
    params = []
    updates = []
    if product_dict.get("name") is not None:
        updates.append("name = %s")
        params.append(product_dict["name"])
    if product_dict.get("price") is not None:
        updates.append("price = %s")
        params.append(product_dict["price"])
    if product_dict.get("category") is not None:
        updates.append("category = %s")
        params.append(product_dict["category"])
    if product_dict.get("active") is not None:
        updates.append("active = %s")
        params.append(product_dict["active"])

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    query += ", ".join(updates) + " WHERE id = %s RETURNING id, name, price, category, active"
    params.append(product_id)

    result = execute_returning_one(query, params)
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return result


@router.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate):
    query = """
        INSERT INTO products (name, price, category, active) VALUES (%s, %s, %s, %s)
        RETURNING id, name, price, category, active
    """
    params = [product.name, product.price, product.category, product.active]

    result = execute_returning_one(query, params)
    return result


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int):
    query = "DELETE FROM products WHERE id = %s RETURNING id"
    try:
        result = execute_returning_one(query, [product_id])
    except (
        psycopg.errors.RestrictViolation,
        psycopg.errors.ForeignKeyViolation
    ):
        raise HTTPException(status_code=409, detail="Cannot delete product with existing orders")
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")


def create_table_products():
    with psycopg.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
                    category TEXT,
                    active BOOLEAN DEFAULT TRUE
                );
            """)


def update_products():
    with psycopg.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
               INSERT INTO products (name, price, active, category)
                VALUES
                    ('grey-t', 30.49, TRUE, 't-shirt'),
                    ('blue-trousers', 99.99, TRUE, 'trousers'),
                    ('red-shirt', 68.56, TRUE, 'shirt-m'),
                    ('black-sweater', 101.48, TRUE, 'sweater-m'),
                    ('white-socks', 5.95, TRUE, 'socks-m'),
                    ('running-shoes', 129.90, TRUE, 'shoes'),
                    ('winter-jacket', 249.00, TRUE, 'jacket'),
                    ('green-t', 35.50, TRUE, 't-shirt'),
                    ('black-trousers', 89.90, FALSE, 'trousers'),
                    ('sports-socks', 12.95, TRUE, 'socks-m');
            """)
