from pathlib import Path
from datetime import datetime
import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent / "models" / "food_expiry.joblib"
DATA_PATH = Path(__file__).resolve().parent / "data" / "expiry_training_data.csv"


def ensure_model():
    if MODEL_PATH.exists():
        return
    train()


def train():
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder

    df = pd.read_csv(DATA_PATH)
    features = ["food_type", "prepared_hour"]
    prep = ColumnTransformer(
        [("food", OneHotEncoder(handle_unknown="ignore"), ["food_type"])],
        remainder="passthrough",
    )
    model = Pipeline([
        ("preprocess", prep),
        ("regressor", RandomForestRegressor(
            n_estimators=180, random_state=42, max_depth=8, min_samples_leaf=2
        )),
    ])
    model.fit(df[features], df["shelf_life_hours"])
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return MODEL_PATH


def predict_expiry_hours(food_type, prepared_at: datetime):
    ensure_model()
    model = joblib.load(MODEL_PATH)
    prepared_hour = prepared_at.hour + prepared_at.minute / 60.0
    X = pd.DataFrame([{"food_type": food_type, "prepared_hour": prepared_hour}])
    hours = float(model.predict(X)[0])
    # Keep the demo model inside a practical food-rescue window.
    hours = max(2.0, min(48.0, hours))
    label = "AI-estimated shelf-life"
    return hours, label


if __name__ == "__main__":
    print(f"Expiry model saved to: {train()}")
