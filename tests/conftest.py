import os
import pytest
from fastapi.testclient import TestClient
import uuid

from app.database import execute_returning_one
from  app.main import app

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def verify_test_database():
    db_name = os.environ.get("DB_NAME")

    if db_name != "learning_test_db":
        pytest.exit(
            f"Tests must use learning_test_db, not {db_name}"
        )


@pytest.fixture(scope="function", autouse=False)
def product_cleanup():
    created_ids = []

    yield created_ids

    for id in created_ids:
        response = client.delete(f"/products/{id}")
        assert response.status_code == 204


def delete_order(order_id: int) -> None:
    query = "DELETE FROM orders WHERE id = %s RETURNING id"

    result = execute_returning_one(query, [order_id])
    if result is None:
        raise ValueError(f"Order {order_id} not found")


def delete_customer(customer_id: int) -> None:
    query = "DELETE FROM customers WHERE id = %s RETURNING id"

    result = execute_returning_one(query, [customer_id])
    if result is None:
        raise ValueError(f"Customer {customer_id} not found")


@pytest.fixture(scope="function", autouse=False)
def order_cleanup():
    created_ids = []

    yield created_ids

    for order_id in created_ids:
        delete_order(order_id)


@pytest.fixture(scope="function", autouse=False)
def customer_with_orders():
    customer_id = 0
    orders = []
    customer_data = {
        "name": "Test Testsson",
        "email": f"testsson-{uuid.uuid4().hex}@example.com",
        "country": "Finland"
    }

    try:
        response = client.post("/customers", json= customer_data)

        assert response.status_code == 201
        data = response.json()
        customer_id = data["id"]

        order_data_1 = {
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                },
                {
                    "product_id": 3,
                    "quantity": 2
                }
            ]
        }
        order_data_2 = {
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": 2,
                    "quantity": 1
                },
                {
                    "product_id": 4,
                    "quantity": 2
                }
            ]
        }

        response = client.post("/orders", json=order_data_1)
        assert response.status_code == 201
        data = response.json()
        orders.append(data["id"])

        response = client.post("/orders", json=order_data_2)
        assert response.status_code == 201
        data = response.json()
        orders.append(data["id"])

        yield {
            "customer_id": customer_id,
            "orders": orders
        }

    finally:
        for order_id in orders:
            delete_order(order_id)

        if customer_id != 0:
            delete_customer(customer_id)
