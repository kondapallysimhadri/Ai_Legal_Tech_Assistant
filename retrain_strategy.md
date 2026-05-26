# 🔁 Continuous Learning & Retraining Strategy

To ensure the AI-Powered Legal Claim Assistant remains accurate as new case law and breach data emerge, we implement a closed-loop MLOps retraining strategy.

## 1. Data Collection & Feedback Loop
*   **User Feedback:** The frontend UI can collect implicit feedback (e.g., if a user proceeds with a claim flagged as "Likely") or explicit feedback ("Was this explanation helpful?").
*   **Outcome Tracking:** When actual legal claims are resolved, the backend updates the MongoDB `ml_dataset` collection with the ground-truth `eligibility_label`.

## 2. Triggering Retraining
*   **Scheduled Pipeline:** A cron job runs every Sunday at 02:00 UTC.
*   **Performance Threshold:** If real-world F1-score drops below 0.75 or Data Drift is detected (e.g., a massive new breach type skews the feature distribution), an immediate alert is sent to the MLOps team via Slack to trigger manual retraining.

## 3. Retraining Workflow (`ml_service/retrain.py`)
1.  **Extract:** Pull the latest 10,000 verified records from MongoDB.
2.  **Preprocess:** Run through `data_pipeline.py`.
3.  **Train (Challenger Model):** Train a new XGBoost model using `GridSearchCV`.
4.  **Evaluate:** Compare the Challenger model against the Champion (production) model using a holdout test set.
5.  **Promote:** If Challenger F1 > Champion F1 + 0.02, automatically promote the Challenger model.

## 4. Model Registry & Versioning
*   We use **MLflow** to track all experiments.
*   Models are saved as `eligibility_v2.pkl`, etc., and tagged in the model registry.
*   The API loader dynamically fetches the model tagged `Production`.

## 5. Rollback Plan
If the new model exhibits unexpected bias or sudden accuracy drop post-deployment, the API instantly falls back to the `N-1` model version cached in the registry.
