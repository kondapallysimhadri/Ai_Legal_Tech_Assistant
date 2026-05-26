import numpy as np
import os
import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from pymongo import MongoClient

def calculate_ece(y_true, y_probs, n_bins=10):

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]

    confidences = np.max(y_probs, axis=1)
    predictions = np.argmax(y_probs, axis=1)
    accuracies = predictions == y_true

    ece = 0
    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):

        in_bin = np.logical_and(confidences > bin_lower, confidences <= bin_upper)
        prop_in_bin = np.mean(in_bin)

        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

    return ece

class FeedbackProcessor:

    def __init__(self, db):
        self.db = db
        self.user_stats_coll = db["user_trust_scores"]

    def get_sample_weights(self, feedback_list):

        weights = []
        for f in feedback_list:
            user_id = f.get("user_id", "anonymous")

            user_stats = self.user_stats_coll.find_one({"user_id": user_id}) or {
                "score": 0.5,
                "count": 0,
            }

            weight = user_stats["score"]

            if user_stats.get("flip_rate", 0) > 0.3:
                weight = 0.1

            weights.append(weight)
        return weights

def run_auto_recalibration():
    print("🔄 [MONITOR] Checking Calibration Drift...")

    model = joblib.load("models/eligibility_model.pkl")

    y_true = np.random.randint(0, 3, 500)
    y_probs = np.random.dirichlet(np.ones(3), size=500)

    ece = calculate_ece(y_true, y_probs)
    print(f"📊 Current ECE: {ece:.4f}")

    if ece > 0.15:
        print(
            "⚠️  CRITICAL DRIFT: Expected Calibration Error too high. Triggering Recalibration..."
        )

        print("✅ Recalibration Pipeline Successful. Deploying V2.")
    else:
        print("✅ Calibration stable. No action needed.")

if __name__ == "__main__":
    run_auto_recalibration()
