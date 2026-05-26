import joblib
import traceback
import os

MODELS_DIR = "models"
files = [
    f"{MODELS_DIR}/preprocessor.pkl",
    f"{MODELS_DIR}/success_model.pkl",
    f"{MODELS_DIR}/success_preprocessor.pkl",
    f"{MODELS_DIR}/eligibility_model.pkl",
    f"{MODELS_DIR}/eligibility_model_us.pkl",
    f"{MODELS_DIR}/eligibility_model_eu.pkl",
    f"{MODELS_DIR}/eligibility_model_india.pkl",
]

for f in files:
    if os.path.exists(f):
        print(f"Loading {f}...")
        try:
            joblib.load(f)
            print("  Loaded successfully!")
        except Exception as e:
            print(f"  ❌ Error loading {f}:")
            traceback.print_exc()
    else:
        print(f"{f} does not exist")
