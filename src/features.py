import pandas as pd
import numpy as np

def engineer_derived_features(df):

    df = df.copy()

    severity_map = {
        "SSN": 10,
        "credit card": 9,
        "Medical Records": 9,
        "password": 7,
        "email": 5,
        "full name": 3,
    }

    df["severity_score"] = df["data_exposed"].map(severity_map).fillna(5)

    df["total_exposure_impact"] = (
        np.log1p(df["records_affected"]) * df["severity_score"]
    )

    df["legal_complexity"] = 0.5
    if "jurisdiction" in df.columns:
        df.loc[df["jurisdiction"] == "EU", "legal_complexity"] += 0.2

    return df
