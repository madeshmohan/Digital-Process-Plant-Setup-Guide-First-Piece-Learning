import pytest
from backend.database.database import init_db, seed_default_products
from data.generate_dataset import generate_synthetic_data
from backend.learning.recommendation_engine import get_recommendations_for_variant

def test_recommendation_engine():
    init_db()
    seed_default_products()
    
    rec = get_recommendations_for_variant("Variant A")
    assert rec["product_variant"] == "Variant A"
    assert rec["min_safe_temp"] <= rec["recommended_temperature"] <= rec["max_safe_temp"]
    assert rec["min_safe_pressure"] <= rec["recommended_pressure"] <= rec["max_safe_pressure"]
    assert rec["sample_size"] >= 0
    assert rec["historical_pass_rate"] >= 0.0
    assert "disclaimer" in rec
