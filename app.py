import streamlit as st
import pandas as pd
import os
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Expense Tracker AI",
    page_icon="💰",
    layout="wide"
)

# ---------------- DARK STYLE ----------------
st.markdown("""
<style>
body { background-color: #0b0e11; }
.main { background-color: #0b0e11; color: white; }
h1, h2, h3 { color: #fcd535; }
.stButton>button {
    background-color: #fcd535;
    color: black;
    font-weight: bold;
    border-radius: 8px;
}
.metric-card {
    background-color: #161a1e;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

FILE_NAME = "expenses.csv"

st.title("💰 Smart Expense Tracker AI Dashboard")

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
        st.metric("💰 Total Spent", f"{total_spent:.2f}")

    with col2:
        st.metric("📊 Average Expense", f"{avg_spent:.2f}")

    with col3:
        st.metric("🔥 Highest Expense", f"{max_spent:.2f}")

    st.divider()

    # -------- MONTHLY BAR CHART --------
    monthly_df = monthly_summary.reset_index()
    monthly_df["Month"] = monthly_df["Month"].astype(str)

    fig_bar = px.bar(
        monthly_df,
        x="Month",
        y="Amount",
        template="plotly_dark",
        color="Amount"
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # -------- CATEGORY DONUT --------
    category_summary = df.groupby("Category")["Amount"].sum().reset_index()

    fig_pie = px.pie(
        category_summary,
        names="Category",
        values="Amount",
        hole=0.5,
        template="plotly_dark"
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

        st.metric("🤖 Next Month Prediction", f"{prediction[0]:.2f}")

else:
    st.info("No expenses added yet. Add from sidebar.")
