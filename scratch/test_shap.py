import joblib
import shap
import traceback
from sklearn.calibration import CalibratedClassifierCV

MODELS_DIR = "/Users/apple/Desktop/ai_legal_assistant/models"

try:
    elig_model = joblib.load(f"{MODELS_DIR}/eligibility_model.pkl")
    print("Loaded eligibility_model.pkl")

    if isinstance(elig_model, CalibratedClassifierCV):
        print("Model is CalibratedClassifierCV")
        base_est = elig_model.calibrated_classifiers_[0].estimator
        print("Extracting base estimator...")
        explainer = shap.TreeExplainer(base_est)
        print("SHAP TreeExplainer created successfully!")
    else:
        print("Model is not calibrated")
        explainer = shap.TreeExplainer(elig_model)
        print("SHAP TreeExplainer created successfully!")
except Exception as e:
    print("❌ Failed SHAP test:")
    traceback.print_exc()
