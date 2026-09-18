import streamlit as st

from tracker_core import get_dataframe, get_session_items


st.set_page_config(page_title="Search Expenses", page_icon="🔎", layout="wide")
st.title("🔎 Search Expenses")

items = get_session_items(st)
df = get_dataframe(items)

if df.empty:
    st.info("No expenses available.")
else:
    keyword = st.text_input("Search description or category")
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start Date", value=df["date"].min().date())
    with col2:
        end_date = st.date_input("End Date", value=df["date"].max().date())

    result = df.copy()
    if keyword:
        description_match = result["description"].str.contains(
            keyword, case=False, na=False
        )
        category_match = result["category"].str.contains(
            keyword, case=False, na=False
        )
        result = result[description_match | category_match]

    result = result[
        (result["date"].dt.date >= start_date)
        & (result["date"].dt.date <= end_date)
    ]

    st.subheader(f"Results: {len(result)}")
    st.dataframe(
        result[["date", "amount", "category", "description"]],
        use_container_width=True,
        hide_index=True
    )
