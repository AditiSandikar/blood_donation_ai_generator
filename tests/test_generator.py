import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from generator import generate_blood_units_dataset, BLOOD_GROUPS
from distribution_learner import learn_parameters
from lifecycle_engine import calculate_daily_inventory

def test_generation_structure():
    records = generate_blood_units_dataset(count=100)
    assert len(records) == 100
    r = records[0]
    expected_keys = [
        "unitId", "donorName", "bloodGroup", "units",
        "collectionDate", "expiryDate", "storageTemperature",
        "hemoglobinLevel", "bloodPressure", "status", "city", "dayIndex"
    ]
    for k in expected_keys:
        assert k in r

def test_blood_groups_valid():
    records = generate_blood_units_dataset(count=500)
    for r in records:
        assert r["bloodGroup"] in BLOOD_GROUPS

def test_shelf_life_42_days():
    records = generate_blood_units_dataset(count=100)
    for r in records:
        coll = datetime.fromisoformat(r["collectionDate"])
        exp = datetime.fromisoformat(r["expiryDate"])
        days = (exp - coll).days
        assert days == 42

def test_speed_benchmark_50k():
    t0 = time.time()
    records = generate_blood_units_dataset(count=50000)
    t1 = time.time()
    elapsed = t1 - t0
    assert len(records) == 50000
    assert elapsed < 3.0  # Must generate 50,000 in under 3 seconds

def test_distribution_learning():
    sample_donors = [
        {"age": 20, "weight": 55.0, "bloodGroup": "O+", "totalDonations": 2, "responseRate": 90},
        {"age": 30, "weight": 75.0, "bloodGroup": "A+", "totalDonations": 4, "responseRate": 80},
    ]
    profile = learn_parameters(sample_donors)
    assert profile["age_mean"] == 25.0
    assert profile["weight_mean"] == 65.0
    assert profile["avg_donations"] == 3.0

def test_daily_inventory_calculation():
    records = generate_blood_units_dataset(count=1000)
    inv = calculate_daily_inventory(records, target_day_offset=0)
    assert "totalSafeUnits" in inv
    assert "stockByBloodGroup" in inv
    assert sum(inv["stockByBloodGroup"].values()) == inv["totalSafeUnits"]

if __name__ == "__main__":
    print("Running tests...")
    test_generation_structure()
    print("✓ test_generation_structure passed")
    test_blood_groups_valid()
    print("✓ test_blood_groups_valid passed")
    test_shelf_life_42_days()
    print("✓ test_shelf_life_42_days passed")
    test_speed_benchmark_50k()
    print("✓ test_speed_benchmark_50k passed")
    test_distribution_learning()
    print("✓ test_distribution_learning passed")
    test_daily_inventory_calculation()
    print("✓ test_daily_inventory_calculation passed")
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
