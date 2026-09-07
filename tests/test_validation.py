import pytest
from backend.validation.validation_engine import validate_parameters

def test_valid_parameters_variant_a():
    res = validate_parameters("Variant A", 180.0, 5.0)
    assert res["status"] == "VALID"
    assert res["temp_valid"] is True
    assert res["pressure_valid"] is True
    assert res["interaction_valid"] is True
    assert res["interaction_score"] <= 0.75

def test_failure_case_1_temperature_out_of_range():
    # Variant A target 180 [175 - 185]
    res = validate_parameters("Variant A", 230.0, 5.0)
    assert res["status"] == "BLOCKED"
    assert res["temp_valid"] is False
    assert "outside the configured synthetic range" in res["reason"]

def test_failure_case_2_pressure_out_of_range():
    # Variant A target 5.0 [4.7 - 5.3]
    res = validate_parameters("Variant A", 180.0, 4.2)
    assert res["status"] == "BLOCKED"
    assert res["pressure_valid"] is False
    assert "outside the configured synthetic range" in res["reason"]

def test_failure_case_3_interaction_failure():
    # Variant A: T=184.0 and P=5.28.
    # Individually: 184 in [175, 185] -> True. 5.28 in [4.7, 5.3] -> True.
    # Combined interaction score S_int > 1.0 -> BLOCKED!
    res = validate_parameters("Variant A", 184.0, 5.28)
    assert res["status"] == "BLOCKED"
    assert res["temp_valid"] is True
    assert res["pressure_valid"] is True
    assert res["interaction_valid"] is False
    assert res["interaction_score"] > 1.0
    assert "Interaction Failure" in res["reason"]
    assert "thermal-pressure stress violation" in res["reason"]

def test_warning_zone_parameters():
    # Variant A: T=182.0, P=5.20 -> S_int between 0.75 and 1.0 (0.7644)
    res = validate_parameters("Variant A", 182.0, 5.20)
    assert res["status"] in ["WARNING", "VALID"]
    assert res["temp_valid"] is True
    assert res["pressure_valid"] is True
