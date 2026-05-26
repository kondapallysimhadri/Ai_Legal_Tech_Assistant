import os
import pandas as pd
from pymongo import MongoClient
from src.predict import LegalPredictor
import json

def validate_system():
    print("⚖️  Starting Real-World Model Validation Layer...")

    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client["legal_ai_db"]
    cases_collection = db["cases"]

    predictor = LegalPredictor()
    if not predictor.is_loaded:
        print("❌ Models not loaded. Please train first.")
        return

    real_cases = list(cases_collection.find().limit(50))
    if not real_cases:
        print("⚠️ No real cases found in DB. Run orchestrator first.")
        return

    validation_results = []
    correct_count = 0

    for case in real_cases:

        input_data = {
            "breach_type": case.get("impact_category", "tech").lower(),
            "data_exposed": case.get("title", "Email"),
            "records_affected": 500000,
            "compensation_amount": 1000,
            "case_type": "breach",
            "jurisdiction": "US",
            "time_since_breach": 30,
            "user_impact_level": "medium",
            "documents_available": 3,
            "proof_strength": "medium",
            "prior_claims": 0,
            "location_match": 1,
            "severity_score": 50,
            "deadline_remaining_days": 100,
            "legal_complexity_score": 5,
            "similarity_to_past_cases": 0.5,
        }

        result = predictor.predict_case(input_data)

        actual_outcome = (
            "Likely Eligible"
            if "Eligible" in case.get("summary", "")
            else "Not Eligible"
        )

        is_correct = result["prediction"] == actual_outcome
        if is_correct:
            correct_count += 1

        validation_results.append(
            {
                "case_id": str(case["_id"]),
                "prediction": result["prediction"],
                "actual_outcome": actual_outcome,
                "is_correct": is_correct,
                "confidence": result["eligibility_confidence"],
                "notes": "Weak-labeled based on AI summary keyword matching.",
            }
        )

    accuracy = (correct_count / len(real_cases)) * 100
    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "total_cases": len(real_cases),
        "accuracy": f"{accuracy:.2f}%",
        "results": validation_results,
    }

    os.makedirs("reports", exist_ok=True)
    with open("reports/real_world_validation.json", "w") as f:
        json.dump(report, f, indent=4)

    print(f"✅ Validation Complete. Real-World Accuracy: {accuracy:.2f}%")
    print(f"📄 Report saved to: reports/real_world_validation.json")

if __name__ == "__main__":
    validate_system()
