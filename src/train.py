import pandas as pd
import numpy as np
import joblib
import os
import warnings

warnings.filterwarnings("ignore")

from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV,
    StratifiedKFold,
    cross_val_score,
)
from sklearn.metrics import f1_score
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBClassifier, XGBRegressor
import datetime

from src.preprocessing import get_preprocessor
from src.evaluate import evaluate_classification, evaluate_regression

DATASET_PATH = "data/unified_legal_dataset.csv"
MODELS_DIR = "models"

NUM_FEATURES = [
    "records_affected",
    "compensation_amount",
    "time_since_breach",
    "documents_available",
    "prior_claims",
    "location_match",
    "severity_score",
    "deadline_remaining_days",
    "legal_complexity_score",
    "similarity_to_past_cases",
]

CAT_FEATURES = [
    "breach_type",
    "data_exposed",
    "case_type",
    "jurisdiction",
    "user_impact_level",
    "proof_strength",
]

def load_and_inspect(path: str) -> pd.DataFrame:

    df = pd.read_csv(path)
    print("=" * 60)
    print("STEP 1 — DATA INSPECTION")
    print("=" * 60)
    print(f"Shape          : {df.shape}")
    print(f"Null values    :\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    if df.isnull().sum().sum() == 0:
        print("  (no nulls)")
    print(f"Data types     :\n{df.dtypes}")
    print(f"\nEligibility distribution:\n{df['eligibility_label'].value_counts()}")
    print(f"\nSuccess probability stats:\n{df['success_probability'].describe()}")
    return df

XGB_CLF_PARAM_GRID = {
    "n_estimators": [100, 200, 300],
    "max_depth": [3, 5, 7],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample": [0.7, 0.8, 1.0],
}

XGB_REG_PARAM_GRID = {
    "n_estimators": [100, 200, 300],
    "max_depth": [3, 5, 7],
    "learning_rate": [0.01, 0.05, 0.1],
}

def train_eligibility(df: pd.DataFrame):

    print("\n" + "=" * 60)
    print("PHASE 1 — ELIGIBILITY MODEL (GENERALIZATION UPGRADE)")
    print("=" * 60)

    X = df[NUM_FEATURES + CAT_FEATURES]
    y = df["eligibility_label"]

    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.176, random_state=42, stratify=y_train_val
    )

    print(f"Splits: Train({len(X_train)}), Val({len(X_val)}), Test({len(X_test)})")

    preprocessor = get_preprocessor(NUM_FEATURES, CAT_FEATURES)
    X_train_prep = preprocessor.fit_transform(X_train)
    X_val_prep = preprocessor.transform(X_val)
    X_test_prep = preprocessor.transform(X_test)

    print("\n🔍 Running Stratified 5-Fold Cross-Validation...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(
        XGBClassifier(eval_metric="mlogloss"),
        X_train_prep,
        y_train,
        cv=skf,
        scoring="f1_weighted",
    )
    print(f"CV F1-Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    class_weights = {0: 1.0, 1: 3.0, 2: 3.0}
    sample_weights = np.array([class_weights[label] for label in y_train])

    base_model = XGBClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4,
        reg_alpha=0.1,
        reg_lambda=1.0,
        eval_metric="mlogloss",
        random_state=42,
    )

    base_model.fit(
        X_train_prep,
        y_train,
        sample_weight=sample_weights,
        eval_set=[(X_val_prep, y_val)],
        verbose=False,
    )

    print("\n⚖️ Calibrating Classifier Probabilities (Isotonic)...")
    calibrated_model = CalibratedClassifierCV(
        estimator=base_model, method="isotonic", cv=3
    )
    calibrated_model.fit(X_train_prep, y_train)

    model = calibrated_model

    train_preds = model.predict(X_train_prep)
    val_preds = model.predict(X_val_prep)
    train_f1 = f1_score(y_train, train_preds, average="weighted")
    val_f1 = f1_score(y_val, val_preds, average="weighted")

    print(f"\n📈 Overfitting Check (Calibrated):")
    print(f"   Train F1: {train_f1:.4f} | Val F1: {val_f1:.4f}")
    if (train_f1 - val_f1) > 0.05:
        print("⚠️  WARNING: High overfitting detected (>5% gap).")
    else:
        print("✅ Generalization looks stable (<5% gap).")

    test_preds = model.predict(X_test_prep)
    test_probs = model.predict_proba(X_test_prep)
    test_metrics = evaluate_classification(
        y_test, test_preds, y_probs=test_probs, model_name="FINAL UNSEEN TEST"
    )

    version = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    joblib.dump(model, f"{MODELS_DIR}/eligibility_model_{version}.pkl")
    joblib.dump(model, f"{MODELS_DIR}/eligibility_model.pkl")
    joblib.dump(preprocessor, f"{MODELS_DIR}/preprocessor.pkl")

    return model, preprocessor

def train_success(df: pd.DataFrame):
    """STEPS 2–8 for the Claim Success Regression model."""
    print("\n" + "=" * 60)
    print("PHASE 2 — SUCCESS MODEL (REGRESSION)")
    print("=" * 60)

    X = df[NUM_FEATURES + CAT_FEATURES]
    y = df["success_probability"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    preprocessor = get_preprocessor(NUM_FEATURES, CAT_FEATURES)
    X_train_prep = preprocessor.fit_transform(X_train)
    X_test_prep = preprocessor.transform(X_test)

    candidates = {
        "Linear Regression": LinearRegression(),
        "Random Forest Regressor": RandomForestRegressor(
            n_estimators=100, random_state=42
        ),
        "XGBoost Regressor": XGBRegressor(
            n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42
        ),
    }

    results = {}
    for name, model in candidates.items():
        model.fit(X_train_prep, y_train)
        preds = model.predict(X_test_prep)
        metrics = evaluate_regression(y_test, preds, name)
        results[name] = {"model": model, "metrics": metrics}

    best_name = min(results, key=lambda k: results[k]["metrics"]["rmse"])
    print(f"\n🏆 Best baseline model (RMSE): {best_name}")

    print("\n⚙️  Tuning XGBoost Regressor …")
    tuner = RandomizedSearchCV(
        XGBRegressor(random_state=42),
        XGB_REG_PARAM_GRID,
        n_iter=12,
        cv=3,
        scoring="neg_root_mean_squared_error",
        random_state=42,
        n_jobs=-1,
        verbose=0,
    )
    tuner.fit(X_train_prep, y_train)

    tuned_model = tuner.best_estimator_
    tuned_preds = tuned_model.predict(X_test_prep)
    tuned_metrics = evaluate_regression(
        y_test, tuned_preds, "XGBoost Regressor (Tuned)"
    )

    if tuned_metrics["rmse"] <= results[best_name]["metrics"]["rmse"]:
        final_model = tuned_model
        print(
            f"\n✅ Tuned XGBoost Regressor selected (RMSE={tuned_metrics['rmse']:.4f})"
        )
        print(f"   Best params: {tuner.best_params_}")
    else:
        final_model = results[best_name]["model"]
        print(
            f"\n✅ {best_name} retained (RMSE={results[best_name]['metrics']['rmse']:.4f})"
        )

    joblib.dump(final_model, f"{MODELS_DIR}/success_model.pkl")
    joblib.dump(preprocessor, f"{MODELS_DIR}/success_preprocessor.pkl")
    print(f"💾 Saved: {MODELS_DIR}/success_model.pkl")
    print(f"💾 Saved: {MODELS_DIR}/success_preprocessor.pkl")

    return final_model, preprocessor

def train_regional_models(df: pd.DataFrame):

    regions = ["global", "US", "EU", "India"]
    models = {}

    for region in regions:
        print(f"\n🌍 Training Model for Jurisdiction: {region.upper()}")

        if region == "global":
            regional_df = df
        else:
            regional_df = df[df["jurisdiction"] == region]

        if len(regional_df) < 50:
            print(f"⚠️  Not enough data for {region}. Skipping.")
            continue

        model, prep = train_eligibility(regional_df)

        suffix = f"_{region.lower()}" if region != "global" else ""
        joblib.dump(model, f"{MODELS_DIR}/eligibility_model{suffix}.pkl")
        models[region] = model

    return models

def run_full_pipeline():
    df = load_and_inspect(DATASET_PATH)

    regional_models = train_regional_models(df)

    succ_model, succ_prep = train_success(df)

    print("\n" + "=" * 60)
    print("✅ MULTI-JURISDICTION PIPELINE COMPLETE")
    print(f"   Generated {len(regional_models)} eligibility models.")
    print("=" * 60)

if __name__ == "__main__":
    run_full_pipeline()
