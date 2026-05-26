import pandas as pd
import numpy as np
import os

def generate_synthetic_data(num_samples=1000):
    np.random.seed(42)

    breach_types = ["Healthcare", "Finance", "Tech", "Retail", "Government"]
    data_exposed_options = [
        "SSN",
        "Email",
        "Password",
        "Credit Card",
        "Full Name",
        "Address",
    ]
    company_types = ["Public", "Private", "Non-profit", "SME"]
    jurisdictions = ["US", "EU", "India", "UK", "Canada"]
    impact_levels = ["Low", "Medium", "High"]

    data = []
    for _ in range(num_samples):
        b_type = np.random.choice(breach_types)
        d_exposed = np.random.choice(
            data_exposed_options, size=np.random.randint(1, 4), replace=False
        ).tolist()
        r_affected = np.random.randint(1000, 10000000)
        c_type = np.random.choice(company_types)
        juris = np.random.choice(jurisdictions)
        time_since = np.random.randint(1, 1000)
        impact = np.random.choice(impact_levels)
        sim_score = np.random.random()

        score = 0
        if "SSN" in d_exposed or "Credit Card" in d_exposed:
            score += 4
        if impact == "High":
            score += 3
        if r_affected > 100000:
            score += 2
        if sim_score > 0.7:
            score += 2

        if score >= 8:
            label = 2
        elif score >= 5:
            label = 1
        else:
            label = 0

        data.append(
            {
                "breach_type": b_type,
                "data_exposed": ",".join(d_exposed),
                "records_affected": r_affected,
                "company_type": c_type,
                "jurisdiction": juris,
                "time_since_breach": time_since,
                "user_impact_level": impact,
                "past_case_similarity_score": sim_score,
                "eligibility_label": label,
            }
        )

    df = pd.DataFrame(data)

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/eligibility_dataset.csv", index=False)
    print(
        f"✅ Synthetic dataset generated with {num_samples} samples: data/eligibility_dataset.csv"
    )
    print(df["eligibility_label"].value_counts())

if __name__ == "__main__":
    generate_synthetic_data()
