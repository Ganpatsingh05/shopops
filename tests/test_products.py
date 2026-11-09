from fastapi.testclient import TestClient

from app.core.config import settings

ADMIN_HEADERS = {
    "X-Admin-API-Key": settings.admin_api_key,
}


def sample_product(sku: str = "SKU-TEST-001") -> dict:
    return {
        "sku": sku,
        "name": "Wireless Mouse",
        "description": "2.4 GHz wireless mouse",
        "price": "799.00",
        "stock": 25,
    }


def create_product(
    client: TestClient,
    sku: str = "SKU-TEST-001",
):
    return client.post(
        "/api/v1/admin/products",
        headers=ADMIN_HEADERS,
        json=sample_product(sku),
    )


def test_create_product(client: TestClient):
    response = create_product(client)

    assert response.status_code == 201

    data = response.json()

    assert data["sku"] == "SKU-TEST-001"
    assert data["name"] == "Wireless Mouse"
    assert data["price"] == "799.00"
    assert data["stock"] == 25
    assert data["is_active"] is True


def test_admin_requires_api_key(client: TestClient):
    response = client.post(
        "/api/v1/admin/products",
        json=sample_product(),
    )

    assert response.status_code == 401


def test_duplicate_sku_returns_conflict(client: TestClient):
    first = create_product(client)
    second = create_product(client)

    assert first.status_code == 201
    assert second.status_code == 409


def test_list_and_search_products(client: TestClient):
    create_product(client)

    response = client.get("/api/v1/products")

    assert response.status_code == 200
    assert len(response.json()) == 1

    search_response = client.get(
        "/api/v1/products",
        params={"search": "mouse"},
    )

    assert search_response.status_code == 200
    assert len(search_response.json()) == 1


def test_get_product(client: TestClient):
    created = create_product(client)
    product_id = created.json()["id"]

    response = client.get(f"/api/v1/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["id"] == product_id


def test_missing_product_returns_404(client: TestClient):
    response = client.get("/api/v1/products/99999")

    assert response.status_code == 404


def test_update_product(client: TestClient):
    created = create_product(client)
    product_id = created.json()["id"]

    response = client.put(
        f"/api/v1/admin/products/{product_id}",
        headers=ADMIN_HEADERS,
        json={
            "price": "749.00",
            "stock": 20,
        },
    )

    assert response.status_code == 200
    assert response.json()["price"] == "749.00"
    assert response.json()["stock"] == 20


def test_negative_stock_is_rejected(client: TestClient):
    product_data = sample_product()
    product_data["stock"] = -5

    response = client.post(
        "/api/v1/admin/products",
        headers=ADMIN_HEADERS,
        json=product_data,
    )

    assert response.status_code == 422