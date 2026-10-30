from conftest import client
from datetime import date
from decimal import Decimal
from app.database import execute_returning_one


def test_get_customer_orders_customer_not_found():
    response = client.get("/customers/999999/orders")

    assert response.status_code == 404
    assert response.json() == {"detail": "Customer 999999 not found"}


def test_get_orders_with_customer_id_1():
    response = client.get("/customers/1/orders")
    data = response.json()
    
    assert response.status_code == 200
    assert len(data) > 0
    for item in data:
        assert item["order_id"] > 0
        assert isinstance(date.fromisoformat(item["order_date"]), date)
        assert isinstance(item["status"], str)
        assert item["status"] in ["pending", "shipped", "completed", "cancelled"]
        total_price = Decimal(item["total_price"])
        assert total_price >= Decimal("0")


def test_get_orders_with_customer_id_4_and_status_pending():
    response = client.get("/customers/4/orders?status=pending")
    data = response.json()
    
    assert response.status_code == 200
    assert len(data) > 0
    for item in data:
        assert item["order_id"] > 0
        assert isinstance(date.fromisoformat(item["order_date"]), date)
        assert isinstance(item["status"], str)
        assert item["status"] == "pending"
        total_price = Decimal(item["total_price"])
        assert total_price >= Decimal("0")


def test_get_orders_with_customer_id_1_date_desc():
    response = client.get("/customers/1/orders")
    assert response.status_code == 200

    data = response.json()
    assert len(data) > 0

    actual_order = [
        (date.fromisoformat(item["order_date"]), item["order_id"])
        for item in data
    ]
    assert actual_order == sorted(actual_order, reverse=True)


def test_get_orders_with_customer_id_for_customer_without_orders():
    response = client.get("/customers/10/orders")
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_orders_with_customer_id_and_status_unknown():
    response = client.get("/customers/4/orders?status=unknown")
    assert response.status_code == 422


def test_get_orders_from_customer_id_with_fixture(customer_with_orders):
    customer_id = customer_with_orders["customer_id"]
    orders = customer_with_orders["orders"]

    response = client.get(f"/customers/{customer_id}/orders")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert {item["order_id"] for item in data} == set(orders)

    for order_id in orders:
        order = execute_returning_one(
            "SELECT customer_id FROM orders WHERE id = %s",
            [order_id],
        )
        assert order["customer_id"] == customer_id

    actual_date_order = [
        (date.fromisoformat(item["order_date"]), item["order_id"]) for item in data
    ]
    assert actual_date_order == sorted(actual_date_order, reverse=True)
