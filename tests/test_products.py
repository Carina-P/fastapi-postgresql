import pytest
from conftest import client

def test_get_product_not_found():
    response = client.get("/products/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_get_product_with_id_1():
    response = client.get("/products/1")
    data = response.json()
    
    assert response.status_code == 200
    assert data["id"] == 1
    assert isinstance(data["name"], str)
    assert len(data["name"]) > 0
    assert isinstance(data["price"], (int, float))
    assert data["price"] >= 0
    assert isinstance(data["active"], bool)


def test_create_product(product_cleanup):
    new_product = {
        "name": "Test Product",
        "price": 149.90,
        "category": "Testing",
        "active": True
    }

    response = client.post("/products", json=new_product)

    assert response.status_code == 201
    response_json = response.json()
    product_cleanup.append(response_json["id"])

    assert response_json["name"] == "Test Product"
    assert response_json["price"] == pytest.approx(149.90) 
    assert response_json["category"] == "Testing"
    assert response_json["active"] is True
    assert response_json["id"] > 0


def test_create_product_invalid_price():
    new_product = {
        "name": "Invalid Product",
        "price": -100,
        "category": "Testing",
        "active": True
    }
    response = client.post("/products", json=new_product)

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(error["loc"][-1] == "price" for error in errors)
 