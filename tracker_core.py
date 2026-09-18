import json
import os

import pandas as pd
from datetime import datetime
from sklearn.tree import DecisionTreeClassifier


DATA_FILE = "expenses.json"

CATS = [
    "General",
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Other"
]


def load_items():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return []


def save_items(items):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(items, file, ensure_ascii=False, indent=2)


def get_dataframe(items):
    columns = ["id", "date", "amount", "category", "description"]

    if not items:
        return pd.DataFrame(columns=columns)

    dataframe = pd.DataFrame(items)
    dataframe["date"] = pd.to_datetime(dataframe["date"], errors="coerce")
    dataframe["amount"] = pd.to_numeric(dataframe["amount"], errors="coerce")
    return dataframe


TRAINING_DATA = [
    [300, 0, "Food"], [450, 1, "Food"], [700, 1, "Food"],
    [250, 0, "Food"], [600, 0, "Food"],
    [200, 0, "Transport"], [350, 0, "Transport"], [500, 1, "Transport"],
    [800, 0, "Transport"], [1200, 1, "Transport"],
    [1000, 1, "Shopping"], [2500, 1, "Shopping"], [3500, 0, "Shopping"],
    [5000, 1, "Shopping"], [1800, 0, "Shopping"],
    [1000, 0, "Bills"], [1500, 0, "Bills"], [2000, 0, "Bills"],
    [2500, 0, "Bills"], [3000, 0, "Bills"],
    [300, 1, "Entertainment"], [500, 1, "Entertainment"],
    [800, 1, "Entertainment"], [1000, 0, "Entertainment"],
    [1500, 1, "Entertainment"],
    [100, 0, "General"], [200, 1, "General"], [400, 0, "General"],
    [600, 1, "General"], [900, 0, "General"],
    [100, 0, "Other"], [500, 1, "Other"], [900, 0, "Other"],
    [1200, 1, "Other"]
]


def train_model():
    features = []
    categories = []

    for amount, weekend, category in TRAINING_DATA:
        features.append([amount, weekend])
        categories.append(category)

    model = DecisionTreeClassifier(max_depth=4, random_state=42)
    model.fit(features, categories)
    return model


MODEL = train_model()


def predict_category(amount, date):
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    weekend = 1 if date_obj.weekday() >= 5 else 0
    features = [[amount, weekend]]

    prediction = MODEL.predict(features)[0]
    probabilities = MODEL.predict_proba(features)[0]
    confidence = max(probabilities) * 100

    return prediction, confidence


def get_session_items(st):
    if "items" not in st.session_state:
        st.session_state["items"] = load_items()
    return st.session_state["items"]


def render_sidebar(st):
    st.sidebar.divider()
    st.sidebar.caption("Smart Expense Tracker v2")
    st.sidebar.caption("Python • Streamlit • JSON • Pandas • ML")
