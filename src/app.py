"""
Flask REST API Microservice
Exposes endpoints for dataset generation, distribution learning,
and daily dynamic inventory analytics.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

try:
    from .generator import generate_blood_units_dataset
    from .distribution_learner import learn_parameters
    from .lifecycle_engine import calculate_daily_inventory
except ImportError:
    from generator import generate_blood_units_dataset
    from distribution_learner import learn_parameters
    from lifecycle_engine import calculate_daily_inventory

app = Flask(__name__)
CORS(app)

# In-memory cache for fast simulation queries
CURRENT_CACHE = {
    "dataset": [],
    "generatedAt": None
}

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Blood Donation AI Dataset & Simulation Engine",
        "cachedRecords": len(CURRENT_CACHE["dataset"])
    })


@app.route("/api/generate-dataset", methods=["POST"])
def generate():
    """Generates synthetic dataset on-demand (e.g. 1k to 80k records)."""
    data = request.get_json() or {}
    count = int(data.get("count", 50000))
    count = min(count, 100000)  # Safe upper cap

    t0 = time.time()
    records = generate_blood_units_dataset(count=count)
    t1 = time.time()

    CURRENT_CACHE["dataset"] = records
    CURRENT_CACHE["generatedAt"] = time.time()

    return jsonify({
        "status": "success",
        "recordsGenerated": len(records),
        "executionTimeSec": round(t1 - t0, 3),
        "sample": records[:10]  # Return preview sample
    })


@app.route("/api/daily-analytics", methods=["GET"])
def daily_analytics():
    """Calculates active stock and flows for a given day offset (-90 to +30)."""
    day_offset = int(request.args.get("dayOffset", 0))

    # Auto-generate baseline dataset if cache is empty
    if not CURRENT_CACHE["dataset"]:
        CURRENT_CACHE["dataset"] = generate_blood_units_dataset(count=50000)

    analytics = calculate_daily_inventory(CURRENT_CACHE["dataset"], target_day_offset=day_offset)
    return jsonify(analytics)


@app.route("/api/learn-and-generate", methods=["POST"])
def learn_and_generate():
    """Learns parameters from real donor inputs and generates matching synthetic records."""
    data = request.get_json() or {}
    real_donors = data.get("donors", [])
    count = int(data.get("count", 1000))

    learned_profile = learn_parameters(real_donors)
    synthetic_records = generate_blood_units_dataset(count=count, learned_profile=learned_profile)

    return jsonify({
        "status": "success",
        "learnedParameters": learned_profile,
        "count": len(synthetic_records),
        "sample": synthetic_records[:10]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
