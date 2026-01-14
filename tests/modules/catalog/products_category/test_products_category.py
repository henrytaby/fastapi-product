from fastapi.testclient import TestClient


def test_create_category(client: TestClient):
    response = client.post(
        "/api/catalog/products_category/",
        json={"name": "Electronics", "description": "Gadgets"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Electronics"
    assert "id" in data


def test_read_categories(client: TestClient):
    client.post("/api/catalog/products_category/", json={"name": "Books"})
    response = client.get("/api/catalog/products_category/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_read_category(client: TestClient):
    res = client.post("/api/catalog/products_category/", json={"name": "Toys"})
    cat_id = res.json()["id"]

    response = client.get(f"/api/catalog/products_category/{cat_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Toys"


def test_delete_category(client: TestClient):
    res = client.post("/api/catalog/products_category/", json={"name": "Temp"})
    cat_id = res.json()["id"]

    del_res = client.delete(f"/api/catalog/products_category/{cat_id}")
    assert del_res.status_code == 200

    get_res = client.get(f"/api/catalog/products_category/{cat_id}")
    assert get_res.status_code == 404
