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

# ---------------- CUSTOM DARK BINANCE STYLE ----------------
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
.stDownloadButton>button {
    background-color: #fcd535;
    color: black;
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

# ---------------- SAFE FILE LOAD ----------------
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["Date", "Category", "Amount"])
    df.to_csv(FILE_NAME, index=False)

try:
    df = pd.read_csv(FILE_NAME)
except:
    df = pd.DataFrame(columns=["Date", "Category", "Amount"])
    df.to_csv(FILE_NAME, index=False)

# ---------------- SIDEBAR ----------------
st.sidebar.header("➕ Add Expense")

date = st.sidebar.date_input("Date")
category = st.sidebar.selectbox(
    "Category",
    ["Food", "Travel", "Bills", "Shopping", "Other"]
)
amount = st.sidebar.number_input("Amount", min_value=0.0, step=50.0)

if st.sidebar.button("Add Expense"):
    new_data = pd.DataFrame(
        [[date, category, amount]],
        columns=["Date", "Category", "Amount"]
    )
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(FILE_NAME, index=False)
    st.sidebar.success("✅ Added Successfully!")
    st.balloons()
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
        <h2>💰 {total_spent:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
        <h3>Average Expense</h3>
        <h2>📊 {avg_spent:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
        <h3>Highest Expense</h3>
        <h2>🔥 {max_spent:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # -------- CHARTS --------
    col4, col5 = st.columns(2)

    # ----- Monthly Bar Chart (TradingView Style) -----
    with col4:
        st.subheader("📊 Monthly Trend")

        monthly_df = monthly_summary.reset_index()
        monthly_df["Month"] = monthly_df["Month"].astype(str)

        fig_bar = px.bar(
            monthly_df,
            x="Month",
            y="Amount",
            template="plotly_dark",
            color="Amount",
            color_continuous_scale=["#0ecb81", "#f6465d"]
        )

        fig_bar.update_layout(
            paper_bgcolor="#0b0e11",
            plot_bgcolor="#0b0e11",
            font_color="white"
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    # ----- Donut Pie Chart -----
    with col5:
        st.subheader("📌 Category Distribution")

        category_summary = df.groupby("Category")["Amount"].sum().reset_index()
        total_amount = category_summary["Amount"].sum()

        fig_pie = px.pie(
            category_summary,
            names="Category",
            values="Amount",
            hole=0.55,
            template="plotly_dark"
        )

        fig_pie.update_traces(
            textinfo="percent+label",
            marker=dict(
                colors=["#fcd535", "#f6465d", "#0ecb81", "#3b82f6", "#a855f7"],
                line=dict(color="#0b0e11", width=2)
            )
        )

        fig_pie.update_layout(
            paper_bgcolor="#0b0e11",
            plot_bgcolor="#0b0e11",
            font_color="white",
            annotations=[
                dict(
                    text=f"💰<br>{total_amount:.0f}",
                    x=0.5,
                    y=0.5,
                    font_size=20,
                    showarrow=False,
                    font_color="white"
                )
            ]
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # -------- AI PREDICTION --------
    if len(monthly_summary) > 1:

        st.subheader("🤖 AI Next Month Prediction")

        months = np.arange(len(monthly_summary)).reshape(-1, 1)
        expenses = monthly_summary.values

        model = LinearRegression()
        model.fit(months, expenses)

        next_month = np.array([[len(monthly_summary)]])
        prediction = model.predict(next_month)

        score = model.score(months, expenses)

        st.metric("Predicted Next Month Expense", f"💰 {prediction[0]:.2f}")
        st.progress(min(int(score * 100), 100))
        st.write(f"Model Confidence (R²): {score:.2f}")

        if prediction[0] > monthly_summary.mean():
            st.warning("⚠️ Possible Overspending Alert!")

    st.divider()

    # -------- DOWNLOAD --------
    st.download_button(
        label="📥 Download Full Report",
        data=df.to_csv(index=False),
        file_name="expense_report.csv",
        mime="text/csv"
    )

else:
    st.info("No expenses added yet. Add from sidebar to begin.")
