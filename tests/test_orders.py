from conftest import client
from app.database import execute_returning_one, fetch_from_db


def count_rows(table_name: str) -> int:
    queries = {
        "orders": "SELECT COUNT(*) AS nor from orders",
        "order_items": "SELECT COUNT(*) AS nor from order_items"
    }

    query = queries[table_name]
    return execute_returning_one(query, [])["nor"]


def test_create_order_with_missing_product_leads_to_rollback():
    before_nor_orders = count_rows("orders")
    before_nor_order_items = count_rows("order_items")

    new_order = {
        "customer_id": 2,
        "items": [
            {
                "product_id": 1,
                "quantity": 2 
            },
            {
                "product_id": 3,
                "quantity": 1
            },
            {
                "product_id": 999,
                "quantity": 1
            }
        ]
    }

    response = client.post("/orders", json=new_order)
    assert response.status_code == 404
    assert response.json()["detail"] == "Product 999 not found"

    after_nor_orders = count_rows("orders")
    after_nor_order_items = count_rows("order_items")
    assert before_nor_orders == after_nor_orders
    assert before_nor_order_items == after_nor_order_items


def test_create_order(order_cleanup):
    before_nor_orders = count_rows("orders")
    before_nor_order_items = count_rows("order_items")
    product_quantity_map = {1:2, 3:1, 6:1}
    items = [{"product_id": product_id, "quantity": quantity} for product_id, quantity in product_quantity_map.items()]
    new_order = {
        "customer_id": 3,
        "items": items
    }
    
    response = client.post("/orders", json=new_order)
    assert response.status_code == 201

    response_json = response.json()
    order_id = response_json["id"]
    order_cleanup.append(order_id)

    query = "SELECT customer_id from orders WHERE id = %s"
    order = execute_returning_one(query, [order_id])
    assert order["customer_id"] == 3

    query = "SELECT product_id as product_id, quantity as quantity from order_items where order_id = %s"
    order_items = fetch_from_db(query, [order_id])
    
    actual_quantities = {item["product_id"]: item["quantity"] for item in order_items}
    assert actual_quantities == product_quantity_map
  
    after_nor_orders = count_rows("orders")
    after_nor_order_items = count_rows("order_items")

    assert after_nor_orders == before_nor_orders + 1
    assert after_nor_order_items == before_nor_order_items + 3


def test_create_order_with_double_product_ids(order_cleanup):
    before_nor_orders = count_rows("orders")
    before_nor_order_items = count_rows("order_items")

    new_order = {
        "customer_id": 5,
        "items": [
            {
                "product_id": 1,
                "quantity": 2
            },
            {
                "product_id": 3,
                "quantity": 1
            },
            {
                "product_id": 3,
                "quantity": 2
            }
        ]
    }
    
    response = client.post("/orders", json=new_order)
    assert response.status_code == 201

    response_json = response.json()
    order_id = response_json["id"]
    order_cleanup.append(order_id)

    query = "SELECT customer_id from orders WHERE id = %s"
    order = execute_returning_one(query, [order_id])
    assert order["customer_id"] == 5

    query = "SELECT product_id as product_id, quantity as quantity from order_items where order_id = %s"
    order_items = fetch_from_db(query, [order_id])

    expected_quantities = {1:2, 3:3}
    actual_quantities = {item["product_id"]: item["quantity"] for item in order_items}
    assert actual_quantities == expected_quantities
    
    after_nor_orders = count_rows("orders")
    after_nor_order_items = count_rows("order_items")

    assert after_nor_orders == before_nor_orders + 1
    assert after_nor_order_items == before_nor_order_items + 2
