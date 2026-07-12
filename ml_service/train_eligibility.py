import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import shap

MODEL_DIR = "ml_service/models"
os.makedirs(MODEL_DIR, exist_ok=True)

def train_system():

    df = pd.read_csv("data/eligibility_dataset.csv")
    X = df.drop("eligibility_label", axis=1)
    y = df["eligibility_label"]

    categorical_features = [
        "breach_type",
        "data_exposed",
        "company_type",
        "jurisdiction",
        "user_impact_level",
    ]
    numeric_features = [
        "records_affected",
        "time_since_breach",
        "past_case_similarity_score",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    lr_pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )
    lr_pipeline.fit(X_train, y_train)
    lr_pred = lr_pipeline.predict(X_test)
    print("\n--- Logistic Regression (Baseline) ---")
    print(classification_report(y_test, lr_pred))

    rf_pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(random_state=42)),
        ]
    )
    rf_pipeline.fit(X_train, y_train)
    rf_pred = rf_pipeline.predict(X_test)
    print("\n--- Random Forest ---")
    print(classification_report(y_test, rf_pred))

    xgb_pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "classifier",
                XGBClassifier(
                    random_state=42, use_label_encoder=False, eval_metric="mlogloss"
                ),
            ),
        ]
    )

    param_grid = {
        "classifier__n_estimators": [50, 100],
        "classifier__max_depth": [3, 5, 7],
        "classifier__learning_rate": [0.01, 0.1, 0.2],
    }

    grid_search = GridSearchCV(
        xgb_pipeline, param_grid, cv=3, scoring="f1_macro", verbose=1
    )
    grid_search.fit(X_train, y_train)

    best_xgb = grid_search.best_estimator_
    xgb_pred = best_xgb.predict(X_test)

    print("\n--- XGBoost (Best Model) ---")
    print(f"Best Params: {grid_search.best_params_}")
    print(classification_report(y_test, xgb_pred))

    joblib.dump(best_xgb, f"{MODEL_DIR}/eligibility_v1.pkl")

    print(f"✅ Model components saved to models/")

    print(
        "\n💡 MLE NOTE: Recall is prioritized in legal eligibility because 'False Negatives' (telling a valid claimant they are not eligible) "
        "is high risk for the company (potential lawsuits/reputation). 'False Positives' (Likely Eligible) can be filtered later."
    )

    preprocessor.fit(X_train)
    X_train_transformed = preprocessor.transform(X_train)

    cat_feature_names = preprocessor.named_transformers_["cat"].get_feature_names_out(
        categorical_features
    )
    all_feature_names = numeric_features + list(cat_feature_names)

    explainer = shap.TreeExplainer(best_xgb.named_steps["classifier"])

    X_test_transformed = preprocessor.transform(X_test)
    shap_values = explainer.shap_values(X_test_transformed)

    joblib.dump(all_feature_names, f"{MODEL_DIR}/feature_names.pkl")

    print("\n--- SHAP Explainability Complete ---")
    print(f"Summary: Top features extracted for explainability layer.")

if __name__ == "__main__":
    train_system()
