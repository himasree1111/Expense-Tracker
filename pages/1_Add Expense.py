import uuid
from datetime import datetime

import streamlit as st

from tracker_core import CATS, get_session_items, predict_category, save_items


st.set_page_config(page_title="Add Expense", page_icon="➕", layout="wide")
st.title("➕ Add Expense")

items = get_session_items(st)
date = st.date_input("Date", datetime.today())
amount = st.number_input("Amount", min_value=0.0, step=10.0)
description = st.text_input("Description", placeholder="Example: Swiggy")

if amount > 0:
    predicted_category, confidence = predict_category(
        amount,
        date.strftime("%Y-%m-%d")
    )
    st.info(
        f"🤖 ML Prediction: **{predicted_category}** "
        f"(confidence: {confidence:.1f}%)"
    )
else:
    predicted_category = "General"

use_prediction = st.checkbox("Use ML predicted category", value=True)
if use_prediction:
    category = predicted_category
    st.write(f"Selected category: **{category}**")
else:
    category = st.selectbox("Category", CATS)

if st.button("Add Expense", type="primary"):
    if amount <= 0:
        st.error("Amount must be greater than 0.")
    elif not description.strip():
        st.error("Please enter a description.")
    else:
        items.append({
            "id": str(uuid.uuid4())[:8],
            "date": date.strftime("%Y-%m-%d"),
            "amount": amount,
            "category": category,
            "description": description.strip()
        })
        save_items(items)
        st.success(f"Expense added successfully! Category: {category}")
