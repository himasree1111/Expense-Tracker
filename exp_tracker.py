import streamlit as st
import json
import os
import uuid
import pandas as pd
import plotly.express as px

from datetime import datetime
from sklearn.tree import DecisionTreeClassifier


# ============================================================
# CONFIGURATION
# ============================================================

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


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide"
)


# ============================================================
# JSON FUNCTIONS
# ============================================================

def load_items():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return []


def save_items(items):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            items,
            f,
            ensure_ascii=False,
            indent=2
        )


# ============================================================
# DATAFRAME
# ============================================================

def get_dataframe(items):

    if not items:
        return pd.DataFrame(
            columns=[
                "id",
                "date",
                "amount",
                "category",
                "description"
            ]
        )

    df = pd.DataFrame(items)
    #to handle empty items
    df["date"] = pd.to_datetime(
        df["date"],errors="coerce")

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    return df


# ============================================================
# ML TRAINING DATA
# ============================================================

# We use simple historical examples so the Decision Tree
# has something to learn from when the user has very few
# personal expenses.

TRAINING_DATA = [
    # amount, weekend, category
    [300, 0, "Food"],
    [450, 1, "Food"],
    [700, 1, "Food"],
    [250, 0, "Food"],
    [600, 0, "Food"],

    [200, 0, "Transport"],
    [350, 0, "Transport"],
    [500, 1, "Transport"],
    [800, 0, "Transport"],
    [1200, 1, "Transport"],

    [1000, 1, "Shopping"],
    [2500, 1, "Shopping"],
    [3500, 0, "Shopping"],
    [5000, 1, "Shopping"],
    [1800, 0, "Shopping"],

    [1000, 0, "Bills"],
    [1500, 0, "Bills"],
    [2000, 0, "Bills"],
    [2500, 0, "Bills"],
    [3000, 0, "Bills"],

    [300, 1, "Entertainment"],
    [500, 1, "Entertainment"],
    [800, 1, "Entertainment"],
    [1000, 0, "Entertainment"],
    [1500, 1, "Entertainment"],

    [100, 0, "General"],
    [200, 1, "General"],
    [400, 0, "General"],
    [600, 1, "General"],
    [900, 0, "General"],

    [100, 0, "Other"],
    [500, 1, "Other"],
    [900, 0, "Other"],
    [1200, 1, "Other"],
]


def train_model():

    X = []
    y = []

    for amount, weekend, category in TRAINING_DATA:
        X.append([amount, weekend])
        y.append(category)

    model = DecisionTreeClassifier(
        max_depth=4,
        random_state=42
    )

    model.fit(X, y)

    return model


model = train_model()


# ============================================================
# ML PREDICTION
# ============================================================

def predict_category(amount, date):

    date_obj = datetime.strptime(
        date,
        "%Y-%m-%d"
    )

    # Saturday = 5
    # Sunday = 6

    weekend = 1 if date_obj.weekday() >= 5 else 0

    prediction = model.predict(
        [[amount, weekend]]
    )[0]

    probabilities = model.predict_proba(
        [[amount, weekend]]
    )[0]

    confidence = max(probabilities) * 100

    return prediction, confidence


# ============================================================
# SESSION STATE
# ============================================================

if "items" not in st.session_state:
    st.session_state["items"] = load_items()


items = st.session_state["items"]


# ============================================================
# TITLE
# ============================================================

st.title("💰 Smart Expense Tracker")

st.caption(
    "Expense management + analytics + Decision Tree category prediction"
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Dashboard",
        "Add Expense",
        "View Expenses",
        "Search Expenses",
        "Budget Limits"
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.header("📊 Dashboard")
    # st.write("DEBUG:", type(items), items)
    df = get_dataframe(items)

    if df.empty:

        st.info(
            "No expenses yet. Add your first expense!"
        )

    else:

        total = df["amount"].sum()

        count = len(df)

        average = df["amount"].mean()

        current_month = datetime.today().strftime("%Y-%m")

        month_df = df[
            df["date"].dt.strftime("%Y-%m")
            == current_month
        ]

        month_total = month_df["amount"].sum()

        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Spending",
            f"₹{total:,.2f}"
        )

        col2.metric(
            "This Month",
            f"₹{month_total:,.2f}"
        )

        col3.metric(
            "Transactions",
            count
        )

        col4.metric(
            "Average Expense",
            f"₹{average:,.2f}"
        )

        st.divider()

        # ----------------------------------------------------
        # CATEGORY CHART
        # ----------------------------------------------------

        st.subheader("Spending by Category")

        category_df = (
            df.groupby("category")["amount"]
            .sum()
            .reset_index()
        )

        col1, col2 = st.columns(2)

        with col1:

            fig = px.pie(
                category_df,
                names="category",
                values="amount",
                title="Category Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ----------------------------------------------------
        # MONTHLY CHART
        # ----------------------------------------------------

        with col2:

            monthly_df = (
                df.assign(
                    month=df["date"].dt.strftime("%Y-%m")
                )
                .groupby("month")["amount"]
                .sum()
                .reset_index()
            )

            fig2 = px.bar(
                monthly_df,
                x="month",
                y="amount",
                title="Monthly Spending"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        # ----------------------------------------------------
        # RECENT EXPENSES
        # ----------------------------------------------------

        st.subheader("Recent Expenses")

        recent = df.sort_values(
            "date",
            ascending=False
        ).head(10)

        st.dataframe(
            recent[
                [
                    "date",
                    "amount",
                    "category",
                    "description"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# ADD EXPENSE
# ============================================================

elif page == "Add Expense":

    st.header("➕ Add Expense")

    date = st.date_input(
        "Date",
        datetime.today()
    )

    amount = st.number_input(
        "Amount",
        min_value=0.0,
        step=10.0
    )

    description = st.text_input(
        "Description",
        placeholder="Example: Swiggy"
    )

    st.write("")

    # --------------------------------------------------------
    # ML PREDICTION
    # --------------------------------------------------------

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
        confidence = 0

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    use_prediction = st.checkbox(
        "Use ML predicted category",
        value=True
    )

    if use_prediction:

        category = predicted_category

        st.write(
            f"Selected category: **{category}**"
        )

    else:

        category = st.selectbox(
            "Category",
            CATS
        )

    # --------------------------------------------------------
    # ADD BUTTON
    # --------------------------------------------------------

    if st.button(
        "Add Expense",
        type="primary"
    ):

        if amount <= 0:

            st.error(
                "Amount must be greater than 0."
            )

        elif not description.strip():

            st.error(
                "Please enter a description."
            )

        else:

            new_item = {
                "id": str(uuid.uuid4())[:8],
                "date": date.strftime("%Y-%m-%d"),
                "amount": amount,
                "category": category,
                "description": description.strip()
            }

            items.append(new_item)

            save_items(items)

            st.session_state.items = items

            st.success(
                f"Expense added successfully! "
                f"Category: {category}"
            )


# ============================================================
# VIEW EXPENSES
# ============================================================

elif page == "View Expenses":

    st.header("📋 All Expenses")

    df = get_dataframe(items)

    if df.empty:

        st.info("No expenses found.")

    else:

        df = df.sort_values(
            "date",
            ascending=False
        )

        st.dataframe(
            df[
                [
                    "id",
                    "date",
                    "amount",
                    "category",
                    "description"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("Delete Expense")

        ids = df["id"].tolist()

        selected_id = st.selectbox(
            "Select expense ID",
            ids
        )

        if st.button(
            "Delete Selected Expense",
            type="secondary"
        ):

            items[:] = [
                item
                for item in items
                if item["id"] != selected_id
            ]

            save_items(items)

            st.session_state.items = items

            st.success(
                "Expense deleted successfully."
            )

            st.rerun()


# ============================================================
# SEARCH
# ============================================================

elif page == "Search Expenses":

    st.header("🔎 Search Expenses")

    df = get_dataframe(items)

    if df.empty:

        st.info("No expenses available.")

    else:

        keyword = st.text_input(
            "Search description or category"
        )

        col1, col2 = st.columns(2)

        with col1:

            start_date = st.date_input(
                "Start Date",
                value=df["date"].min().date()
            )

        with col2:

            end_date = st.date_input(
                "End Date",
                value=df["date"].max().date()
            )

        result = df.copy()

        if keyword:

            mask = (
                result["description"]
                .str.contains(
                    keyword,
                    case=False,
                    na=False
                )
                |
                result["category"]
                .str.contains(
                    keyword,
                    case=False,
                    na=False
                )
            )

            result = result[mask]

        result = result[
            (result["date"].dt.date >= start_date)
            &
            (result["date"].dt.date <= end_date)
        ]

        st.subheader(
            f"Results: {len(result)}"
        )

        st.dataframe(
            result[
                [
                    "date",
                    "amount",
                    "category",
                    "description"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# BUDGET LIMITS
# ============================================================

elif page == "Budget Limits":

    st.header("⚠️ Budget Limits")

    df = get_dataframe(items)

    if df.empty:

        st.info(
            "Add some expenses first."
        )

    else:

        daily_limit = st.number_input(
            "Daily Spending Limit",
            min_value=0.0,
            step=100.0
        )

        weekly_limit = st.number_input(
            "Weekly Spending Limit",
            min_value=0.0,
            step=100.0
        )

        if st.button(
            "Check Limits"
        ):

            today = datetime.today().date()

            # ------------------------------------------------
            # DAILY
            # ------------------------------------------------

            today_total = df[
                df["date"].dt.date == today
            ]["amount"].sum()

            # ------------------------------------------------
            # WEEKLY
            # ------------------------------------------------

            current_year, current_week, _ = (
                today.isocalendar()
            )

            weekly_total = 0

            for _, row in df.iterrows():

                expense_date = row["date"].date()

                year, week, _ = (
                    expense_date.isocalendar()
                )

                if (
                    year == current_year
                    and week == current_week
                ):

                    weekly_total += row["amount"]

            # ------------------------------------------------
            # RESULTS
            # ------------------------------------------------

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Today's Spending",
                    f"₹{today_total:,.2f}"
                )

                if (
                    daily_limit > 0
                    and today_total > daily_limit
                ):

                    st.error(
                        "⚠️ Daily limit exceeded!"
                    )

                else:

                    st.success(
                        "Daily limit is okay."
                    )

            with col2:

                st.metric(
                    "This Week",
                    f"₹{weekly_total:,.2f}"
                )

                if (
                    weekly_limit > 0
                    and weekly_total > weekly_limit
                ):

                    st.error(
                        "⚠️ Weekly limit exceeded!"
                    )

                else:

                    st.success(
                        "Weekly limit is okay."
                    )


# ============================================================
# SIDEBAR INFORMATION
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "Smart Expense Tracker v2"
)

st.sidebar.caption(
    "Python • Streamlit • JSON • Pandas • ML"
)