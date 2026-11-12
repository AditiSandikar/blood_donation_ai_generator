"""
Distribution Learner
Extracts empirical statistical parameters (Gaussian, Poisson, Categorical, Beta)
from real donor data entered on the platform.
"""
import statistics
from typing import List, Dict, Any

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
# Realistic Indian demographic blood group weights (fallback baseline)
DEFAULT_BG_WEIGHTS = {
    'A+': 0.22, 'A-': 0.015,
    'B+': 0.32, 'B-': 0.025,
    'AB+': 0.09, 'AB-': 0.01,
    'O+': 0.30, 'O-': 0.02
}

def learn_parameters(real_donors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes statistical parameters from real donor entries.
    Falls back gracefully to clinical standards if sample size is small.
    """
    if not real_donors or len(real_donors) < 2:
        return {
            "age_mean": 26.5,
            "age_stdev": 6.8,
            "weight_mean": 64.0,
            "weight_stdev": 9.5,
            "avg_donations": 2.5,
            "avg_response_rate": 88.0,
            "bg_distribution": DEFAULT_BG_WEIGHTS,
            "sample_size": len(real_donors) if real_donors else 0
        }

    # Extract numerical fields safely
    ages = [d.get("age", 25) for d in real_donors if isinstance(d.get("age"), (int, float))]
    weights = [d.get("weight", 65.0) for d in real_donors if isinstance(d.get("weight"), (int, float))]
    donations = [d.get("totalDonations", 1) for d in real_donors if isinstance(d.get("totalDonations"), (int, float))]
    rates = [d.get("responseRate", 85) for d in real_donors if isinstance(d.get("responseRate"), (int, float))]

    # Blood group frequency
    bg_counts = {bg: 0.01 for bg in BLOOD_GROUPS}
    for d in real_donors:
        bg = d.get("bloodGroup")
        if bg in bg_counts:
            bg_counts[bg] += 1

    total_counts = sum(bg_counts.values())
    bg_dist = {bg: round(cnt / total_counts, 4) for bg, cnt in bg_counts.items()}

    return {
        "age_mean": round(statistics.mean(ages) if ages else 26.5, 2),
        "age_stdev": round(statistics.stdev(ages) if len(ages) > 1 else 6.0, 2),
        "weight_mean": round(statistics.mean(weights) if weights else 64.0, 2),
        "weight_stdev": round(statistics.stdev(weights) if len(weights) > 1 else 9.0, 2),
        "avg_donations": round(statistics.mean(donations) if donations else 2.5, 2),
        "avg_response_rate": round(statistics.mean(rates) if rates else 88.0, 2),
        "bg_distribution": bg_dist,
        "sample_size": len(real_donors)
    }
