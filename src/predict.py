import joblib
import pandas as pd
import numpy as np
# import shap
import os
from sklearn.calibration import CalibratedClassifierCV

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

LABEL_MAP = {0: "Not Eligible", 1: "Likely Eligible", 2: "Eligible"}

class LegalPredictor:
    """Wraps both models and provides unified prediction + explanation."""

    def __init__(self):
        self.elig_model = None
        self.elig_prep = None
        self.succ_model = None
        self.succ_prep = None
        self.elig_explainer = None
        self.is_loaded = False
        self._load()

    def _load(self):
        try:

            self.elig_prep = joblib.load(f"{MODELS_DIR}/preprocessor.pkl")
            self.succ_model = joblib.load(f"{MODELS_DIR}/success_model.pkl")
            self.succ_prep = joblib.load(f"{MODELS_DIR}/success_preprocessor.pkl")

            self.model_paths = {
                "global": f"{MODELS_DIR}/eligibility_model.pkl",
                "us": f"{MODELS_DIR}/eligibility_model_us.pkl",
                "eu": f"{MODELS_DIR}/eligibility_model_eu.pkl",
                "india": f"{MODELS_DIR}/eligibility_model_india.pkl",
            }
            self.loaded_models = {"global": joblib.load(self.model_paths["global"])}

            self.elig_model = self.loaded_models["global"]

            try:
                if isinstance(self.elig_model, CalibratedClassifierCV):
                    base_est = self.elig_model.calibrated_classifiers_[0].estimator
                    self.elig_explainer = shap.TreeExplainer(base_est)
                    self._is_calibrated = True
                else:
                    self.elig_explainer = shap.TreeExplainer(self.elig_model)
                    self._is_calibrated = False
            except Exception as shap_err:
                print(f"⚠️  SHAP explainer init failed (non-fatal): {shap_err}")
                self.elig_explainer = None
                self._is_calibrated = isinstance(self.elig_model, CalibratedClassifierCV)

            self.is_loaded = True
            print(
                "✅ Production model engine initialized (Global model loaded, regional models set to Lazy)."
            )
        except Exception as e:
            print(f"⚠️  Could not load models: {e}")

    def _get_routed_model(self, jurisdiction: str):
        """STEP 3B: Routing Logic with Lazy Loading."""
        key = jurisdiction.lower()

        if key in self.loaded_models:
            return self.loaded_models[key]

        if key in self.model_paths and os.path.exists(self.model_paths[key]):
            print(f"📦 [LAZY LOAD] Loading regional model for {key.upper()}...")
            self.loaded_models[key] = joblib.load(self.model_paths[key])
            return self.loaded_models[key]

        return self.loaded_models["global"]

    @staticmethod
    def _feature_names(preprocessor):
        names = []
        for tag, transformer, cols in preprocessor.transformers_:
            if tag == "num":
                names.extend(cols)
            elif tag == "cat":

                ohe = transformer.named_steps["onehot"]
                names.extend(ohe.get_feature_names_out(cols))
        return names

    def _explain(self, X_processed, pred_idx) -> list:
        if self.elig_explainer is None:
            return ["Assessment based on breach severity and jurisdiction."]
        try:
            sv = self.elig_explainer.shap_values(X_processed)
            instance = sv[pred_idx][0] if isinstance(sv, list) else sv[0]

            feat_names = self._feature_names(self.elig_prep)
            impacts = sorted(
                zip(feat_names, instance),
                key=lambda x: abs(x[1]),
                reverse=True,
            )

            explanations = []
            for feat, val in impacts[:5]:
                direction = "increased" if val > 0 else "decreased"
                clean = feat.replace("cat__", "").replace("num__", "").replace("_", " ")
                explanations.append(f"{clean.title()} {direction} eligibility.")
            return explanations
        except Exception as e:
            print(f"SHAP error: {e}")
            return ["Assessment based on overall case severity."]

    def predict_case(self, input_json: dict) -> dict:
        """
        Predicts eligibility and success with:
        - Jurisdiction-based routing (Step 3)
        - Latency-optimized SHAP (Step 4C)
        - Calibrated probabilities
        """
        if not self.is_loaded:
            raise RuntimeError("Models not loaded. Run training first.")

        df = pd.DataFrame([input_json])
        jurisdiction = input_json.get("jurisdiction", "global")

        model = self._get_routed_model(jurisdiction)
        X_e = self.elig_prep.transform(df)
        pred_idx = int(model.predict(X_e)[0])
        probs = model.predict_proba(X_e)[0]
        confidence = float(probs[pred_idx])
        model_prediction_label = LABEL_MAP.get(pred_idx, "Unknown")

        X_s = self.succ_prep.transform(df)
        success = float(np.clip(self.succ_model.predict(X_s)[0], 0, 1))

        if confidence > 0.95:
            explanation = ["Strong match with high-confidence historical precedents."]
        else:
            explanation = self._explain(X_e, pred_idx)

        uncertainty_flag = "low"
        fallback_msg = None
        missing_fields = []

        if confidence >= 0.75:
            uncertainty_flag = "low"
        elif confidence >= 0.50:
            uncertainty_flag = "medium"
            fallback_msg = (
                "Caution: This is a borderline case. AI confidence is moderate."
            )
        else:
            uncertainty_flag = "high"
            fallback_msg = (
                "Uncertain: Need more information to make a reliable decision."
            )
            required = ["records_affected", "time_since_breach", "proof_strength"]
            missing_fields = [
                f
                for f in required
                if input_json.get(f) is None or input_json.get(f) == ""
            ]

        explanation = self._explain(X_e, pred_idx)

        return {
            "prediction": (
                model_prediction_label if uncertainty_flag != "high" else "Uncertain"
            ),
            "model_prediction": f"{model_prediction_label} ({confidence:.0%})",
            "confidence": round(confidence, 4),
            "calibrated": getattr(self, "_is_calibrated", False),
            "success_probability": round(success, 4),
            "uncertainty": uncertainty_flag,
            "explanation": explanation,
            "fallback_message": fallback_msg,
            "missing_fields": missing_fields,
            "disclaimer": "This is AI guidance, not legal advice.",
        }

if __name__ == "__main__":
    predictor = LegalPredictor()

    sample = {
        "breach_type": "finance",
        "data_exposed": "SSN",
        "records_affected": 5_000_000,
        "compensation_amount": 5000,
        "case_type": "lawsuit",
        "jurisdiction": "US",
        "time_since_breach": 45,
        "user_impact_level": "high",
        "documents_available": 4,
        "proof_strength": "high",
        "prior_claims": 0,
        "location_match": 1,
        "severity_score": 75,
        "deadline_remaining_days": 90,
        "legal_complexity_score": 6,
        "similarity_to_past_cases": 0.85,
    }

    result = predictor.predict_case(sample)

    print("\n" + "=" * 50)
    print("PREDICTION RESULT")
    print("=" * 50)
    print(f"Eligibility       : {result['prediction']}")
    print(f"Confidence        : {result['eligibility_confidence']:.1%}")
    print(f"Success Prob.     : {result['success_probability']:.1%}")
    print("Top Decision Drivers:")
    for r in result["explanation"]:
        print(f"  → {r}")
