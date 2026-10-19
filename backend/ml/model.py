from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent / "models" / "rescue_priority.joblib"


def ensure_model():
    if MODEL_PATH.exists():
        return
    from .train_model import train
    train()


def load_model():
    ensure_model()
    return joblib.load(MODEL_PATH)


def predict(payload):
    model = load_model()
    X = pd.DataFrame([payload])
    result = model.predict(X)[0]
    score = float(max(0, min(100, result)))
    label = (
        "CRITICAL" if score >= 80
        else "HIGH" if score >= 60
        else "MEDIUM" if score >= 35
        else "LOW"
    )
    return score, label
