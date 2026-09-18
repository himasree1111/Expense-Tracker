import streamlit as st

from tracker_core import get_dataframe, get_session_items, save_items


st.set_page_config(page_title="View Expenses", page_icon="📋", layout="wide")
st.title("📋 All Expenses")

items = get_session_items(st)
df = get_dataframe(items)

if df.empty:
    st.info("No expenses found.")
else:
    df = df.sort_values("date", ascending=False)
    st.dataframe(
        df[["id", "date", "amount", "category", "description"]],
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("Delete Expense")
    selected_id = st.selectbox("Select expense ID", df["id"].tolist())

    if st.button("Delete Selected Expense", type="secondary"):
        items[:] = [item for item in items if item["id"] != selected_id]
        save_items(items)
        st.success("Expense deleted successfully.")
        st.rerun()
