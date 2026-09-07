import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.database import init_db, seed_default_products

client = TestClient(app)

def setup_module(module):
    init_db()
    seed_default_products()

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    assert "disclaimer" in res.json()

def test_get_products_endpoint():
    res = client.get("/api/products")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 4
    variants = [d["product_variant"] for d in data]
    assert "Variant A" in variants

def test_validate_endpoint():
    payload = {"product_variant": "Variant A", "temperature": 180.0, "pressure": 5.0}
    res = client.post("/api/validate", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "VALID"

def test_validate_interaction_failure_endpoint():
    payload = {"product_variant": "Variant A", "temperature": 184.0, "pressure": 5.28}
    res = client.post("/api/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "BLOCKED"
    assert data["interaction_valid"] is False

def test_recommendation_endpoint():
    res = client.get("/api/recommendations/Variant A")
    assert res.status_code == 200
    assert res.json()["product_variant"] == "Variant A"

def test_analytics_endpoints():
    res_exp = client.get("/api/analytics/experiment")
    assert res_exp.status_code == 200
    assert "baseline" in res_exp.json()

    res_err = client.get("/api/analytics/error-analysis")
    assert res_err.status_code == 200
    assert "category_breakdown" in res_err.json()
