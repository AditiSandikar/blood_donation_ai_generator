"""
Dataset Generator
High-speed Monte Carlo generator for tabular synthetic donor and time-series blood units.
Capable of generating 50k–80k records in under 1 second.
"""
import random
import time
import argparse
import csv
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

try:
    from .distribution_learner import learn_parameters, BLOOD_GROUPS, DEFAULT_BG_WEIGHTS
except ImportError:
    from distribution_learner import learn_parameters, BLOOD_GROUPS, DEFAULT_BG_WEIGHTS

FIRST_NAMES = [
    "Rahul", "Priya", "Aditi", "Rohan", "Sneha", "Vikram", "Ananya", "Karthik",
    "Pooja", "Deepak", "Aarav", "Megha", "Suresh", "Divya", "Nikhil", "Neha"
]
LAST_NAMES = [
    "Sharma", "Rao", "Patil", "Shetty", "Suvarna", "Verma", "Nair", "Kulkarni",
    "Hegde", "Gowda", "Bhat", "Shenoy", "Fernandes", "Kamath", "Deshmukh"
]
CITIES = ["Mangalore", "Bangalore", "Udupi", "Manipal", "Surathkal", "Mysore", "Hubli"]

def generate_blood_units_dataset(
    count: int = 80000,
    days_span: int = 120,
    learned_profile: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Generates a large-scale time-series blood units dataset (50k-80k).
    Each unit contains clinical safety metrics and follows a 42-day lifespan.
    """
    profile = learned_profile or learn_parameters([])
    bg_dist = profile.get("bg_distribution", DEFAULT_BG_WEIGHTS)
    bg_keys = list(bg_dist.keys())
    bg_weights = list(bg_dist.values())

    today = datetime.utcnow()
    records = []

    for i in range(count):
        # Sample day offset: from -90 days ago to +30 days future
        day_offset = random.randint(-90, 30)
        collection_date = today + timedelta(days=day_offset, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        expiry_date = collection_date + timedelta(days=42)  # 42-day RBC shelf life

        blood_group = random.choices(bg_keys, weights=bg_weights, k=1)[0]
        units = 1 if random.random() < 0.85 else 2

        # Clinical screening values
        hb = round(random.gauss(13.8, 1.1), 1)
        sys_bp = int(random.gauss(120, 9))
        dia_bp = int(random.gauss(80, 7))
        storage_temp = round(random.uniform(2.5, 5.5), 1)

        # Status determined by dates relative to simulated today
        if collection_date > today:
            status = 'scheduled_drive'
        elif expiry_date < today:
            status = 'expired'
        else:
            # 65% of active inventory is consumed before expiring
            status = 'used' if random.random() < 0.65 else 'safe'

        records.append({
            "unitId": f"BLD-{1000000 + i}",
            "donorName": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            "bloodGroup": blood_group,
            "units": units,
            "collectionDate": collection_date.isoformat(),
            "expiryDate": expiry_date.isoformat(),
            "storageTemperature": storage_temp,
            "hemoglobinLevel": hb,
            "bloodPressure": f"{sys_bp}/{dia_bp}",
            "status": status,
            "city": random.choice(CITIES),
            "dayIndex": day_offset
        })

    return records


def export_to_csv(records: List[Dict[str, Any]], filepath: str) -> None:
    """Exports records to a CSV file."""
    if not records:
        return
    headers = list(records[0].keys())
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic blood units dataset")
    parser.add_argument("--count", type=int, default=80000, help="Number of records to generate (e.g. 50000 to 80000)")
    parser.add_argument("--output", type=str, default="data/sample_synthetic_output.csv", help="Output CSV path")
    args = parser.parse_args()

    print(f"🚀 Starting generation of {args.count:,} synthetic blood units...")
    t0 = time.time()
    dataset = generate_blood_units_dataset(count=args.count)
    t1 = time.time()
    print(f"✅ Generated {len(dataset):,} records in {t1 - t0:.2f} seconds!")

    if args.output:
        print(f"💾 Exporting to {args.output}...")
        export_to_csv(dataset[:1000], args.output)  # Export sample of 1k to avoid huge file
        print(f"✅ Sample exported successfully to {args.output}")
