from datetime import datetime

import plotly.express as px
import streamlit as st

from tracker_core import get_dataframe, get_session_items, render_sidebar


st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide"
)

items = get_session_items(st)

st.title("💰 Smart Expense Tracker")
st.caption("Expense management + analytics + Decision Tree category prediction")

st.header("📊 Dashboard")
df = get_dataframe(items)

if df.empty:
    st.info("No expenses yet. Add your first expense!")
else:
    total = df["amount"].sum()
    count = len(df)
    average = df["amount"].mean()
    current_month = datetime.today().strftime("%Y-%m")
    month_df = df[df["date"].dt.strftime("%Y-%m") == current_month]
    month_total = month_df["amount"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Spending", f"₹{total:,.2f}")
    col2.metric("This Month", f"₹{month_total:,.2f}")
    col3.metric("Transactions", count)
    col4.metric("Average Expense", f"₹{average:,.2f}")

    st.divider()
    st.subheader("Spending by Category")
    category_df = df.groupby("category")["amount"].sum().reset_index()
    col1, col2 = st.columns(2)

    with col1:
        category_chart = px.pie(
            category_df,
            names="category",
            values="amount",
            title="Category Distribution"
        )
        st.plotly_chart(category_chart, use_container_width=True)

    with col2:
        monthly_df = (
            df.assign(month=df["date"].dt.strftime("%Y-%m"))
            .groupby("month")["amount"]
            .sum()
            .reset_index()
        )
        monthly_chart = px.bar(
            monthly_df,
            x="month",
            y="amount",
            title="Monthly Spending"
        )
        st.plotly_chart(monthly_chart, use_container_width=True)

    st.subheader("Recent Expenses")
    recent = df.sort_values("date", ascending=False).head(10)
    st.dataframe(
        recent[["date", "amount", "category", "description"]],
        use_container_width=True,
        hide_index=True
    )

render_sidebar(st)
