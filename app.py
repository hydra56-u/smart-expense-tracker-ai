import streamlit as st
import pandas as pd
import os
import numpy as np
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Expense Dashboard",
    page_icon="💼",
    layout="wide"
)

# ---------------- MODERN LIGHT THEME ----------------
st.markdown("""
<style>
body {
    background-color: #f5f7fa;
}
.main {
    background-color: #f5f7fa;
}
.sidebar .sidebar-content {
    background-color: white;
}
.card {
    background-color: white;
    padding: 25px;
    border-radius: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}
h1 {
    color: #111827;
}
.metric-title {
    color: #6b7280;
    font-size: 14px;
}
.metric-value {
    font-size: 24px;
    font-weight: bold;
    color: #111827;
}
</style>
""", unsafe_allow_html=True)

FILE_NAME = "expenses.csv"

# ---------------- LOAD FILE ----------------
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["Date", "Category", "Amount"])
    df.to_csv(FILE_NAME, index=False)

df = pd.read_csv(FILE_NAME)

st.title("💼 Expense Dashboard")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📂 Navigation")
menu = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Add Expense"]
)

if menu == "Add Expense":

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("➕ Add Expense")

    date = st.date_input("Date")
    category = st.selectbox(
        "Category",
        ["Food", "Travel", "Bills", "Shopping", "Other"]
    )
    amount = st.number_input("Amount", min_value=0.0)

    if st.button("Save Expense"):
        new_data = pd.DataFrame(
            [[date, category, amount]],
            columns=["Date", "Category", "Amount"]
        )
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(FILE_NAME, index=False)
        st.success("✅ Expense Saved")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":

    if len(df) > 0:

        df["Date"] = pd.to_datetime(df["Date"])
        df["Month"] = df["Date"].dt.to_period("M")

        total_spent = df["Amount"].sum()
        avg_spent = df["Amount"].mean()
        max_spent = df["Amount"].max()

        # -------- TOP METRIC CARDS --------
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="card">
                <div class="metric-title">Total Expenses</div>
                <div class="metric-value">₹ {total_spent:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="card">
                <div class="metric-title">Average Expense</div>
                <div class="metric-value">₹ {avg_spent:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="card">
                <div class="metric-title">Highest Expense</div>
                <div class="metric-value">₹ {max_spent:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # -------- PIE CHART --------
        category_summary = df.groupby("Category")["Amount"].sum().reset_index()

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Expense Distribution")

        fig = px.pie(
            category_summary,
            names="Category",
            values="Amount",
            hole=0.55,
            color_discrete_sequence=px.colors.sequential.Blues
        )

        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font_color="#111827"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.info("No expenses added yet.")
