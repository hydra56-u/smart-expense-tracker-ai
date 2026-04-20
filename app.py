import streamlit as st
import pandas as pd
import os
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Expense Tracker Pro",
    page_icon="💰",
    layout="wide"
)

# ---------------- CUSTOM THEME ----------------
st.markdown("""
<style>

/* Background Gradient */
body {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}

/* Main text */
.main {
    color: white;
}

/* Headers */
h1, h2, h3 {
    color: #fcd535;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111827;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #fcd535, #0ecb81);
    color: black;
    font-weight: bold;
    border-radius: 10px;
    border: none;
    padding: 8px 16px;
    transition: 0.3s;
}
.stButton>button:hover {
    transform: scale(1.05);
    opacity: 0.9;
}

/* Metric Cards */
.metric-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.1);
}

/* Divider spacing */
hr {
    border: 1px solid rgba(255,255,255,0.1);
}

</style>
""", unsafe_allow_html=True)

FILE_NAME = "expenses.csv"

st.title("💰 Smart Expense Tracker Pro")

# ---------------- FILE SETUP ----------------
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["Date", "Category", "Amount"])
    df.to_csv(FILE_NAME, index=False)

df = pd.read_csv(FILE_NAME)

# ---------------- SIDEBAR ----------------
st.sidebar.header("➕ Add Expense")

date = st.sidebar.date_input("Date")
category = st.sidebar.selectbox(
    "Category",
    ["Food", "Travel", "Bills", "Shopping", "Other"]
)
amount = st.sidebar.number_input("Amount", min_value=0.0)

if st.sidebar.button("Add Expense"):
    new_data = pd.DataFrame(
        [[date, category, amount]],
        columns=["Date", "Category", "Amount"]
    )
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(FILE_NAME, index=False)
    st.sidebar.success("✅ Expense Added")
    st.rerun()

# ---------------- MAIN DASHBOARD ----------------
if len(df) > 0:

    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M")

    monthly_summary = df.groupby("Month")["Amount"].sum()

    total_spent = df["Amount"].sum()
    avg_spent = df["Amount"].mean()
    max_spent = df["Amount"].max()

    # -------- KPI CARDS --------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <h3>Total Spent</h3>
        <h2 style='color:#0ecb81'>💰 {total_spent:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
        <h3>Average Expense</h3>
        <h2 style='color:#fcd535'>📊 {avg_spent:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
        <h3>Highest Expense</h3>
        <h2 style='color:#f6465d'>🔥 {max_spent:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # -------- MONTHLY CHART --------
    monthly_df = monthly_summary.reset_index()
    monthly_df["Month"] = monthly_df["Month"].astype(str)

    fig_bar = px.bar(
        monthly_df,
        x="Month",
        y="Amount",
        template="plotly_dark",
        color="Amount",
        color_continuous_scale=["#0ecb81", "#fcd535"]
    )

    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # -------- CATEGORY DONUT --------
    category_summary = df.groupby("Category")["Amount"].sum().reset_index()
    total_amount = category_summary["Amount"].sum()

    fig_pie = px.pie(
        category_summary,
        names="Category",
        values="Amount",
        hole=0.6,
        template="plotly_dark",
        color_discrete_sequence=["#fcd535", "#0ecb81", "#3b82f6", "#f6465d", "#a855f7"]
    )

    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        annotations=[dict(
            text=f"<b>💰 {total_amount:.0f}</b>",
            x=0.5, y=0.5,
            font_size=20,
            showarrow=False,
            font_color="white"
        )]
    )

    st.plotly_chart(fig_pie, use_container_width=True)

    # -------- AI PREDICTION --------
    if len(monthly_summary) > 1:

        months = np.arange(len(monthly_summary)).reshape(-1, 1)
        expenses = monthly_summary.values

        model = LinearRegression()
        model.fit(months, expenses)

        next_month = np.array([[len(monthly_summary)]])
        prediction = model.predict(next_month)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.metric("🤖 Next Month Prediction", f"{prediction[0]:.2f}")

else:
    st.info("No expenses added yet. Add from sidebar.")
