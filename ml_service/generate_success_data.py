import pandas as pd
import numpy as np
import os

def generate_success_dataset(n_samples=1000):
    np.random.seed(42)

    data = {
        "breach_type": np.random.choice(
            ["healthcare", "finance", "tech", "retail"], n_samples
        ),
        "data_exposed": np.random.choice(
            ["SSN", "email", "password", "credit card", "full name"], n_samples
        ),
        "records_affected": np.random.lognormal(
            mean=10, sigma=2, size=n_samples
        ).astype(int),
        "jurisdiction": np.random.choice(["US", "EU", "India", "Global"], n_samples),
        "user_impact_level": np.random.choice(["low", "medium", "high"], n_samples),
        "documents_available": np.random.randint(0, 10, n_samples),
        "proof_strength": np.random.choice(["low", "medium", "high"], n_samples),
        "past_case_similarity_score": np.random.uniform(0, 1, n_samples),
        "legal_complexity_score": np.random.uniform(0, 1, n_samples),
    }

    df = pd.DataFrame(data)

    def calculate_success(row):
        score = 0.2

        if row["user_impact_level"] == "high":
            score += 0.2
        elif row["user_impact_level"] == "medium":
            score += 0.1

        if row["proof_strength"] == "high":
            score += 0.25
        elif row["proof_strength"] == "medium":
            score += 0.15

        if row["data_exposed"] in ["SSN", "credit card"]:
            score += 0.15

        score += min(row["documents_available"] * 0.03, 0.2)

        score += row["past_case_similarity_score"] * 0.1

        score += np.random.normal(0, 0.05)

        return max(0, min(1, score))

    df["success_probability"] = df.apply(calculate_success, axis=1)

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/success_dataset.csv", index=False)
    print(
        f"✅ Success dataset generated with {n_samples} samples: data/success_dataset.csv"
    )

if __name__ == "__main__":
    generate_success_dataset()
