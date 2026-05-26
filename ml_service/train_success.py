import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
import os

def train_success_model():

    if not os.path.exists("data/success_dataset.csv"):
        from ml_service.generate_success_data import generate_success_dataset

        generate_success_dataset()

    df = pd.read_csv("data/success_dataset.csv")

    X = df.drop("success_probability", axis=1)
    y = df["success_probability"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    num_features = [
        "records_affected",
        "documents_available",
        "past_case_similarity_score",
        "legal_complexity_score",
    ]
    cat_features = [
        "breach_type",
        "data_exposed",
        "jurisdiction",
        "user_impact_level",
        "proof_strength",
    ]

    preprocessor = ColumnTransformer(
        [
            ("num", StandardScaler(), num_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features),
        ]
    )

    model = Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "regressor",
                XGBRegressor(
                    n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42
                ),
            ),
        ]
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)

    print(f"📊 Success Model Evaluation:")
    print(f"   RMSE: {rmse:.4f}")
    print(f"   R2 Score: {r2:.4f}")

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/success_model.pkl")

    joblib.dump(preprocessor, "models/success_preprocessor.pkl")

    print("✅ Success model and preprocessor saved to models/")

if __name__ == "__main__":
    train_success_model()
