import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from sklearn.preprocessing import LabelEncoder
import numpy as np

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

def get_data():

    client = MongoClient(MONGO_URI)
    db = client["legal_ai_db"]
    data = list(db["ml_dataset"].find())
    return pd.DataFrame(data)

def preprocess_data(df):

    if df.empty:
        return df, None

    df["records_affected"] = df["records_affected"].fillna(0)
    df["time_since_breach"] = df["time_since_breach"].fillna(12)
    df["legal_precedent_score"] = df["legal_precedent_score"].fillna(0.5)

    df["num_data_exposed"] = df["data_exposed"].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )

    sensitive_keywords = ["SSN", "Medical", "Credit", "Financial", "Social Security"]
    df["has_sensitive_data"] = df["data_exposed"].apply(
        lambda x: (
            1
            if isinstance(x, list)
            and any(
                any(k.lower() in item.lower() for k in sensitive_keywords) for item in x
            )
            else 0
        )
    )

    categorical_cols = ["breach_type", "company_type", "jurisdiction"]
    encoders = {}
    for col in categorical_cols:
        df[col] = df[col].fillna("Unknown")
        le = LabelEncoder()
        df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    if "eligibility_label" in df.columns:
        label_map = {"Not Eligible": 0, "Likely": 1, "Eligible": 2}
        df["target"] = df["eligibility_label"].map(label_map).fillna(0)

    features = [
        "records_affected",
        "time_since_breach",
        "legal_precedent_score",
        "num_data_exposed",
        "has_sensitive_data",
        "breach_type_encoded",
        "company_type_encoded",
        "jurisdiction_encoded",
    ]

    return df, features, encoders

if __name__ == "__main__":
    df = get_data()
    if not df.empty:
        processed_df, features, _ = preprocess_data(df)
        print(f"✅ Processed {len(processed_df)} records.")
        print(f"Features: {features}")
        print(processed_df[features + ["target"]].head())
    else:
        print("❌ No data found.")
