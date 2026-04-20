import streamlit as st
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Expense Tracker AI",
    page_icon="💰",
    layout="centered"
)

FILE_NAME = "expenses.csv"

st.title("💰 Smart Expense Tracker + AI Predictor")

# ---------------- SAFE FILE LOAD ----------------
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["Date", "Category", "Amount"])
    df.to_csv(FILE_NAME, index=False)

try:
    df = pd.read_csv(FILE_NAME)
except:
    df = pd.DataFrame(columns=["Date", "Category", "Amount"])
    df.to_csv(FILE_NAME, index=False)

# ---------------- ADD EXPENSE ----------------
st.subheader("➕ Add New Expense")

col1, col2 = st.columns(2)

with col1:
    date = st.date_input("Select Date")

with col2:
    category = st.selectbox(
        "Category",
        ["Food", "Travel", "Bills", "Shopping", "Other"]
    )

amount = st.number_input("Amount", min_value=0.0, step=50.0)

if st.button("Add Expense"):
    new_data = pd.DataFrame(
        [[date, category, amount]],
        columns=["Date", "Category", "Amount"]
    )
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(FILE_NAME, index=False)
    st.success("✅ Expense Added Successfully!")
    st.rerun()

# ---------------- SHOW DATA ----------------
st.subheader("📋 All Expenses")
st.dataframe(df, use_container_width=True)

# ---------------- ANALYSIS ----------------
if len(df) > 0:

    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M")

    monthly_summary = df.groupby("Month")["Amount"].sum()

    # ----- Monthly Chart -----
    st.subheader("📊 Monthly Expense Summary")
    st.bar_chart(monthly_summary)

    # ----- Category Pie Chart -----
    st.subheader("📌 Expense Distribution by Category")

    category_summary = df.groupby("Category")["Amount"].sum()

    fig, ax = plt.subplots()
    ax.pie(
        category_summary,
        labels=category_summary.index,
        autopct="%1.1f%%"
    )
    ax.set_title("Expenses by Category")

    st.pyplot(fig)

    # ----- Budget System -----
    st.subheader("🎯 Set Monthly Budget")

    budget = st.number_input(
        "Enter Your Monthly Budget",
        min_value=0.0
    )

    if budget > 0:
        current_month_expense = monthly_summary.iloc[-1]

        st.write(f"Current Month Spending: 💰 {current_month_expense:.2f}")

        if current_month_expense > budget:
            st.error("🚨 You have exceeded your budget!")
        else:
            st.success("✅ You are within your budget.")

    # ----- AI Prediction -----
    if len(monthly_summary) > 1:

        st.subheader("🤖 AI Next Month Spending Prediction")

        months = np.arange(len(monthly_summary)).reshape(-1, 1)
        expenses = monthly_summary.values

        model = LinearRegression()
        model.fit(months, expenses)

        next_month = np.array([[len(monthly_summary)]])
        prediction = model.predict(next_month)

        st.write(f"🔮 Predicted Next Month Expense: 💰 {prediction[0]:.2f}")

        score = model.score(months, expenses)
        st.write(f"📈 Model Accuracy (R² Score): {score:.2f}")

        if prediction[0] > monthly_summary.mean():
            st.warning("⚠️ Warning: You may overspend next month!")

    # ----- Download Report -----
    st.subheader("📥 Download Report")

    st.download_button(
        label="Download Expenses as CSV",
        data=df.to_csv(index=False),
        file_name="expense_report.csv",
        mime="text/csv"
    )