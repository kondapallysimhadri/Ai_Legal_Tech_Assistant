from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    mean_squared_error,
    r2_score,
    classification_report,
    brier_score_loss,
)
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def evaluate_classification(y_true, y_pred, y_probs=None, model_name="Model"):

    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average="weighted"),
        "recall": recall_score(y_true, y_pred, average="weighted"),
        "f1": f1_score(y_true, y_pred, average="weighted"),
    }

    if y_probs is not None:

        brier_scores = []
        for i in range(len(np.unique(y_true))):
            y_true_binary = (y_true == i).astype(int)
            brier_scores.append(brier_score_loss(y_true_binary, y_probs[:, i]))
        metrics["brier_score"] = np.mean(brier_scores)

    print(f"\n📊 --- {model_name} CLASSIFICATION REPORT ---")
    print(classification_report(y_true, y_pred))

    if "brier_score" in metrics:
        print(f"Brier Score: {metrics['brier_score']:.4f} (Calibration Quality)")

    cm = confusion_matrix(y_true, y_pred)
    print("Confusion Matrix:")
    print(cm)

    print(
        f"\n💡 Rationale: Recall ({metrics['recall']:.2f}) is critical. Missing an eligible claimant leads to lost legal rights."
    )

    return metrics

def evaluate_regression(y_true, y_pred, model_name="Model"):

    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    print(f"\n📈 --- {model_name} REGRESSION REPORT ---")
    print(f"RMSE: {rmse:.4f}")
    print(f"R² Score: {r2:.4f}")

    return {"rmse": rmse, "r2": r2}
