import pandas as pd
import numpy as np
import os

def generate_unified_dataset(n_samples=1500):
    np.random.seed(42)

    breach_types = ["healthcare", "finance", "tech", "retail"]
    data_exposed_options = ["SSN", "email", "password", "credit_card"]
    case_types = ["breach", "lawsuit", "settement"]
    jurisdictions = ["US", "EU", "India"]

    breach_type = np.random.choice(breach_types, n_samples)
    data_exposed = np.random.choice(data_exposed_options, n_samples)
    records_affected = np.random.randint(1000, 10000000, n_samples)
    compensation_amount = np.random.randint(100, 10000, n_samples)
    case_type = np.random.choice(case_types, n_samples)
    jurisdiction = np.random.choice(jurisdictions, n_samples)
    time_since_breach = np.random.randint(1, 365, n_samples)

    user_impact_level = np.random.choice(["low", "medium", "high"], n_samples)
    documents_available = np.random.randint(0, 6, n_samples)
    proof_strength = np.random.choice(["low", "medium", "high"], n_samples)
    prior_claims = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    location_match = np.random.choice([0, 1], n_samples, p=[0.3, 0.7])

    severity_score = np.zeros(n_samples)
    for i in range(n_samples):
        base_score = 50 if data_exposed[i] in ["SSN", "credit_card"] else 20
        size_bonus = min(50, (records_affected[i] / 10000000) * 50)
        severity_score[i] = int(base_score + size_bonus)

    deadline_remaining_days = np.random.randint(0, 180, n_samples)
    legal_complexity_score = np.random.randint(1, 11, n_samples)
    similarity_to_past_cases = np.round(np.random.uniform(0, 1, n_samples), 2)

    eligibility_label = np.zeros(n_samples, dtype=int)
    success_probability = np.zeros(n_samples)

    for i in range(n_samples):

        elig_score = 0

        if data_exposed[i] in ["SSN", "credit_card"] and severity_score[i] > 60:
            elig_score += 3
        if user_impact_level[i] == "high":
            elig_score += 2
        if time_since_breach[i] < 180:
            elig_score += 1

        if deadline_remaining_days[i] == 0:
            elig_label = 0
        elif elig_score >= 4:
            elig_label = 2
        elif elig_score >= 2:
            elig_label = 1
        else:
            elig_label = 0

        eligibility_label[i] = elig_label

        if elig_label == 0:
            succ_prob = 0.0
        else:
            succ_score = 0.3

            if proof_strength[i] == "high" and documents_available[i] >= 3:
                succ_score += 0.3
            elif proof_strength[i] == "medium":
                succ_score += 0.15

            succ_score += similarity_to_past_cases[i] * 0.2

            if location_match[i] == 1:
                succ_score += 0.1

            if prior_claims[i] == 1:
                succ_score -= 0.1

            succ_score += np.random.normal(0, 0.05)

            succ_prob = max(0.0, min(1.0, succ_score))

        success_probability[i] = round(succ_prob, 4)

    df = pd.DataFrame(
        {
            "breach_type": breach_type,
            "data_exposed": data_exposed,
            "records_affected": records_affected,
            "compensation_amount": compensation_amount,
            "case_type": case_type,
            "jurisdiction": jurisdiction,
            "time_since_breach": time_since_breach,
            "user_impact_level": user_impact_level,
            "documents_available": documents_available,
            "proof_strength": proof_strength,
            "prior_claims": prior_claims,
            "location_match": location_match,
            "severity_score": severity_score,
            "deadline_remaining_days": deadline_remaining_days,
            "legal_complexity_score": legal_complexity_score,
            "similarity_to_past_cases": similarity_to_past_cases,
            "eligibility_label": eligibility_label,
            "success_probability": success_probability,
        }
    )

    class_0 = df[df["eligibility_label"] == 0]
    class_1 = df[df["eligibility_label"] == 1]
    class_2 = df[df["eligibility_label"] == 2]

    min_len = min(len(class_0), len(class_1), len(class_2))

    if min_len > 0:
        balanced_df = (
            pd.concat(
                [
                    class_0.sample(min_len, random_state=42),
                    class_1.sample(min_len, random_state=42),
                    class_2.sample(min_len, random_state=42),
                ]
            )
            .sample(frac=1, random_state=42)
            .reset_index(drop=True)
        )
    else:
        balanced_df = df

    os.makedirs("data", exist_ok=True)
    balanced_df.to_csv("data/unified_legal_dataset.csv", index=False)

    return balanced_df

if __name__ == "__main__":
    df = generate_unified_dataset()
    print("Dataset generated successfully at data/unified_legal_dataset.csv")
    print("\nClass Distribution:")
    print(df["eligibility_label"].value_counts())
