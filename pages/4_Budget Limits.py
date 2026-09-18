from datetime import datetime

import streamlit as st

from tracker_core import get_dataframe, get_session_items


st.set_page_config(page_title="Budget Limits", page_icon="⚠️", layout="wide")
st.title("⚠️ Budget Limits")

items = get_session_items(st)
df = get_dataframe(items)

if df.empty:
    st.info("Add some expenses first.")
else:
    daily_limit = st.number_input("Daily Spending Limit", min_value=0.0, step=100.0)
    weekly_limit = st.number_input("Weekly Spending Limit", min_value=0.0, step=100.0)

    if st.button("Check Limits"):
        today = datetime.today().date()
        today_total = df[df["date"].dt.date == today]["amount"].sum()
        current_year, current_week, _ = today.isocalendar()
        weekly_total = sum(
            row["amount"]
            for _, row in df.iterrows()
            if row["date"].date().isocalendar()[:2]
            == (current_year, current_week)
        )

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Today's Spending", f"₹{today_total:,.2f}")
            if daily_limit > 0 and today_total > daily_limit:
                st.error("⚠️ Daily limit exceeded!")
            else:
                st.success("Daily limit is okay.")

        with col2:
            st.metric("This Week", f"₹{weekly_total:,.2f}")
            if weekly_limit > 0 and weekly_total > weekly_limit:
                st.error("⚠️ Weekly limit exceeded!")
            else:
                st.success("Weekly limit is okay.")
