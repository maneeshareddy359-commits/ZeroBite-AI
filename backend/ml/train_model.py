from pathlib import Path
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "training_data.csv"
MODEL_DIR = BASE / "models"
OUT = MODEL_DIR / "rescue_priority.joblib"


def train():
    MODEL_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(DATA)

    # The project no longer asks donors for latitude/longitude, so distance is
    # intentionally not an ML input. Priority is driven by information the
    # application can actually know: food type, quantity, remaining rescue
    # window, donor reliability and current demand/scarcity.
    features = [
        "food_type",
        "quantity_meals",
        "hours_to_expiry",
        "donor_reliability",
        "demand_level",
    ]
    prep = ColumnTransformer(
        [("food", OneHotEncoder(handle_unknown="ignore"), ["food_type"])],
        remainder="passthrough",
    )
    model = Pipeline(
        [
            ("preprocess", prep),
            ("regressor", RandomForestRegressor(
                n_estimators=300,
                random_state=42,
                max_depth=10,
                min_samples_leaf=1,
            )),
        ]
    )
    model.fit(df[features], df["rescue_priority"])
    joblib.dump(model, OUT)
    return OUT


if __name__ == "__main__":
    print(f"Trained model saved to: {train()}")
