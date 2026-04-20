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

# ---------------- DATABASE SETUP ----------------
conn = sqlite3.connect("expense_app.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users(
            email TEXT PRIMARY KEY,
            password TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS expenses(
            email TEXT,
            date TEXT,
            category TEXT,
            amount REAL)""")

conn.commit()

# ---------------- PASSWORD HASH ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- LOGIN PAGE ----------------
if st.session_state.user is None:

    st.markdown("""
    <style>
    body {background-color: #f3f4f6;}
    .login-container {
        display:flex;
        justify-content:center;
        align-items:center;
        height:90vh;
    }
    .login-card {
        background:white;
        padding:40px;
        border-radius:16px;
        width:400px;
        box-shadow:0 15px 40px rgba(0,0,0,0.15);
    }
    .login-title {
        font-size:26px;
        font-weight:bold;
        margin-bottom:20px;
        text-align:center;
    }
    .social-btn {
        width:100%;
        padding:10px;
        border-radius:8px;
        border:1px solid #ddd;
        margin-bottom:10px;
        background-color:white;
        cursor:pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    st.markdown("<div class='login-title'>🔐 Sign In</div>", unsafe_allow_html=True)

    st.markdown("<button class='social-btn'>🌍 Continue with Google</button>", unsafe_allow_html=True)
    st.markdown("<button class='social-btn'> Continue with Apple</button>", unsafe_allow_html=True)
    st.markdown("<hr>OR", unsafe_allow_html=True)

    email = st.text_input("Email address")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            hashed = hash_password(password)
            c.execute("SELECT * FROM users WHERE email=? AND password=?",
                      (email, hashed))
            if c.fetchone():
                st.session_state.user = email
                st.success("✅ Login Successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with col2:
        if st.button("Register"):
            hashed = hash_password(password)
            try:
                c.execute("INSERT INTO users VALUES (?,?)", (email, hashed))
                conn.commit()
                st.success("✅ Account Created! Now Login")
            except:
                st.error("User already exists")

    st.markdown("</div></div>", unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
else:

    # -------- DARK THEME --------
    st.markdown("""
    <style>
    body { background-color: #0b0e11; }
    .main { background-color: #0b0e11; color: white; }
    h1, h2, h3 { color: #fcd535; }
    .metric-card {
        background-color: #161a1e;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.success(f"Logged in as {st.session_state.user}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    st.title("💰 Smart Expense Tracker AI")

    # -------- ADD EXPENSE --------
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
        st.sidebar.success("Added ✅")
        st.balloons()
        st.rerun()

    # -------- LOAD USER DATA --------
    df = pd.read_sql_query(
        "SELECT * FROM expenses WHERE email=?",
        conn,
        params=(st.session_state.user,)
    )

    if len(df) > 0:

        df["date"] = pd.to_datetime(df["date"])
        df["Month"] = df["date"].dt.to_period("M")

        monthly_summary = df.groupby("Month")["amount"].sum()

        total_spent = df["amount"].sum()
        avg_spent = df["amount"].mean()

        col1, col2 = st.columns(2)

        with col1:
            st.metric("💰 Total Spent", f"{total_spent:.2f}")

        with col2:
            st.metric("📊 Average Expense", f"{avg_spent:.2f}")

        # -------- MONTHLY CHART --------
        monthly_df = monthly_summary.reset_index()
        monthly_df["Month"] = monthly_df["Month"].astype(str)

        fig_bar = px.bar(
            monthly_df,
            x="Month",
            y="amount",
            template="plotly_dark",
            color="amount"
        )

        st.plotly_chart(fig_bar, use_container_width=True)

        # -------- CATEGORY DONUT --------
        category_summary = df.groupby("category")["amount"].sum().reset_index()

        fig_pie = px.pie(
            category_summary,
            names="category",
            values="amount",
            hole=0.55,
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
        st.info("No expenses added yet.")
