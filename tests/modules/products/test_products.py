from fastapi.testclient import TestClient

def test_create_product(client: TestClient):
    response = client.post(
        "/api/products/",
        json={"title": "Test Product", "price": 100, "description": "A test product", "image": "http://img"}
    )
    # Note: If brand_id validation fails due to real DB connection, we verify 500 or validation error.
    # Ideally should mock valid brand. But creating without brand should pass if optional.
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Product"
    assert "id" in data

def test_read_products(client: TestClient):
    response = client.post(
        "/api/products/",
        json={"title": "Product 1", "price": 10, "image": "img"}
    )
    assert response.status_code == 201
    
    response = client.get("/api/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_read_product(client: TestClient):
    res_create = client.post(
        "/api/products/",
        json={"title": "Unique Product", "price": 50, "image": "img"}
    )
    product_id = res_create.json()["id"]

    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Unique Product"

def test_update_product(client: TestClient):
    res_create = client.post(
        "/api/products/",
        json={"title": "Old Name", "price": 20, "image": "img"}
    )
    product_id = res_create.json()["id"]

    response = client.patch(
        f"/api/products/{product_id}",
        json={"title": "New Name"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "New Name"

def test_delete_product(client: TestClient):
    res_create = client.post(
        "/api/products/",
        json={"title": "To Delete", "price": 20, "image": "img"}
    )
    product_id = res_create.json()["id"]

    response = client.delete(f"/api/products/{product_id}")
    assert response.status_code == 200
    
    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 404
