import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Expense Tracker AI",
    page_icon="💰",
    layout="wide"
)

# ---------------- CUSTOM DARK THEME ----------------
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
.login-box {
    background-color: #161a1e;
    padding: 40px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 0 20px #fcd53533;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("expense_app.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users(
            username TEXT,
            password TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS expenses(
            username TEXT,
            date TEXT,
            category TEXT,
            amount REAL)""")

conn.commit()

# ---------------- PASSWORD HASH ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- LOGIN SYSTEM ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.title("🔐 Login / Register")

    option = st.radio("Select Option", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Register":
        if st.button("Create Account"):
            hashed = hash_password(password)
            c.execute("INSERT INTO users VALUES (?,?)", (username, hashed))
            conn.commit()
            st.success("✅ Account Created Successfully")

    if option == "Login":
        if st.button("Login"):
            hashed = hash_password(password)
            c.execute("SELECT * FROM users WHERE username=? AND password=?",
                      (username, hashed))
            data = c.fetchone()
            if data:
                st.session_state.user = username
                st.success("✅ Login Successful")
                st.rerun()
            else:
                st.error("❌ Invalid Credentials")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
else:

    st.sidebar.success(f"Logged in as {st.session_state.user}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    st.title("💰 Smart Expense Tracker AI")

    # -------- Add Expense --------
    st.sidebar.header("➕ Add Expense")

    date = st.sidebar.date_input("Date")
    category = st.sidebar.selectbox(
        "Category",
        ["Food", "Travel", "Bills", "Shopping", "Other"]
    )
    amount = st.sidebar.number_input("Amount", min_value=0.0)

    if st.sidebar.button("Add Expense"):
        c.execute("INSERT INTO expenses VALUES (?,?,?,?)",
                  (st.session_state.user, str(date), category, amount))
        conn.commit()
        st.sidebar.success("✅ Added Successfully")
        st.balloons()
        st.rerun()

    # -------- Load User Data --------
    df = pd.read_sql_query(
        f"SELECT * FROM expenses WHERE username='{st.session_state.user}'",
        conn
    )

    if len(df) > 0:

        df["date"] = pd.to_datetime(df["date"])
        df["Month"] = df["date"].dt.to_period("M")

        monthly_summary = df.groupby("Month")["amount"].sum()

        total_spent = df["amount"].sum()

        st.metric("Total Spent", f"💰 {total_spent:.2f}")

        # -------- Monthly Chart --------
        monthly_df = monthly_summary.reset_index()
        monthly_df["Month"] = monthly_df["Month"].astype(str)

        fig = px.bar(
            monthly_df,
            x="Month",
            y="amount",
            template="plotly_dark",
            color="amount"
        )

        fig.update_layout(
            paper_bgcolor="#0b0e11",
            plot_bgcolor="#0b0e11",
            font_color="white"
        )

        st.plotly_chart(fig, use_container_width=True)

        # -------- Category Donut --------
        category_summary = df.groupby("category")["amount"].sum().reset_index()

        fig2 = px.pie(
            category_summary,
            names="category",
            values="amount",
            hole=0.55,
            template="plotly_dark"
        )

        st.plotly_chart(fig2, use_container_width=True)

        # -------- AI Prediction --------
        if len(monthly_summary) > 1:

            months = np.arange(len(monthly_summary)).reshape(-1, 1)
            expenses = monthly_summary.values

            model = LinearRegression()
            model.fit(months, expenses)

            next_month = np.array([[len(monthly_summary)]])
            prediction = model.predict(next_month)

            st.metric("Next Month Prediction", f"💰 {prediction[0]:.2f}")

    else:
        st.info("No expenses yet.")
