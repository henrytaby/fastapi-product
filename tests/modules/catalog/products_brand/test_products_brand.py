from fastapi.testclient import TestClient


def test_create_brand(client: TestClient):
    response = client.post(
        "/api/catalog/product_brand/",
        json={"name": "Sony", "description": "Electronics Giant"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sony"
    assert "id" in data


def test_read_brands(client: TestClient):
    client.post("/api/catalog/product_brand/", json={"name": "Nike"})
    response = client.get("/api/catalog/product_brand/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_read_brand(client: TestClient):
    res = client.post("/api/catalog/product_brand/", json={"name": "Adidas"})
    brand_id = res.json()["id"]

    response = client.get(f"/api/catalog/product_brand/{brand_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Adidas"


def test_delete_brand(client: TestClient):
    res = client.post("/api/catalog/product_brand/", json={"name": "Puma"})
    brand_id = res.json()["id"]

    del_res = client.delete(f"/api/catalog/product_brand/{brand_id}")
    assert del_res.status_code == 200

    get_res = client.get(f"/api/catalog/product_brand/{brand_id}")
    assert get_res.status_code == 404
