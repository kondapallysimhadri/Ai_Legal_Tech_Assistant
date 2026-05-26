import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

MODEL_PATH = "ml_service/models/eligibility_v1.pkl"
FEATURE_NAMES_PATH = "ml_service/models/feature_names.pkl"

app = FastAPI(title="AI Legal Claim ML Service")

class UserData(BaseModel):
    breach_type: str
    data_exposed: str
    records_affected: int
    company_type: str
    jurisdiction: str
    time_since_breach: int
    user_impact_level: str
    past_case_similarity_score: float

model = None
feature_names = None

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    feature_names = joblib.load(FEATURE_NAMES_PATH)

def get_explanation(data: UserData, prediction: int):
    """Logic to derive top contributing factors for explanation."""
    explanation = []

    if prediction >= 1:
        if "SSN" in data.data_exposed or "Credit Card" in data.data_exposed:
            explanation.append("Highly sensitive data (SSN/Credit Card) exposed")
        if data.records_affected > 100000:
            explanation.append("Significant breach severity (High records count)")
        if data.user_impact_level == "High":
            explanation.append("High individual impact level reported")
        if data.past_case_similarity_score > 0.7:
            explanation.append("Strong correlation with settled past cases")

    if not explanation:
        explanation = ["General assessment based on breach parameters"]

    return explanation

@app.post("/predict")
async def predict(data: UserData):
    if model is None:
        raise HTTPException(
            status_code=500, detail="Model not loaded. Please run training first."
        )

    input_df = pd.DataFrame([data.dict()])

    try:
        pred_idx = model.predict(input_df)[0]
        probs = model.predict_proba(input_df)[0]
        confidence = float(probs[pred_idx])

        labels = ["Not Eligible", "Likely Eligible", "Eligible"]
        prediction = labels[pred_idx]

        explanation = get_explanation(data, pred_idx)

        return {
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "explanation": explanation,
            "metadata": {"model_version": "v1.0", "status": "Inference Complete"},
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
