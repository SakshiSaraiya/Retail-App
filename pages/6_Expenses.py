import streamlit as st
import pandas as pd
from db_connector import get_connection
from datetime import date
import plotly.express as px

# --- Page Config ---
st.set_page_config(
    page_title="Expense Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Modern CSS Styling ---
st.markdown("""
    <style>
    body, [data-testid="stAppViewContainer"] {
        background-color: #f7f9fb;
    }
    [data-testid="stSidebar"] {
        background-color: #14213d;
    }
    [data-testid="stSidebar"] * {
        color: #f9fafb !important;
        font-size: 1.08rem;
    }
    .main-card {
        background: #fff;
        border-radius: 18px;
        box-shadow: 0 2px 16px rgba(20,33,61,0.08);
        padding: 2rem 2.5rem 2rem 2.5rem;
        margin-bottom: 2.5rem;
    }
    h1, h2, h3, h5, label, p, div {
        color: #14213d !important;
    }
    .stTextInput input, .stDateInput input, .stSelectbox, .stNumberInput input {
        background: #f3f7fa !important;
        border-radius: 6px !important;
    }
    .stButton > button {
        background: #2563eb;
        color: #fff;
        padding: 0.5rem 1.5rem;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.07rem;
        transition: 0.15s;
    }
    .stButton > button:hover {
        background: #1d4ed8;
        color: #e0e7ef;
        font-weight: 700;
    }
    .stDataFrame div {
        font-size: 1rem;
        color: #111 !important;
    }
    .section-title {
        font-size: 1.32rem;
        font-weight: 600;
        margin-bottom: 1rem;
        letter-spacing: 0.03em;
        color: #10284e;
    }
    </style>
""", unsafe_allow_html=True)

# --- Page Title ---
st.markdown('<h1 style="margin-top:1rem;">Spending Tracker</h1>', unsafe_allow_html=True)
st.write("Log and manage your income and expenses.")

# --- DB Connection ---
conn = get_connection()
cursor = conn.cursor()

# --- Add New Transaction Card ---
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Add New Transaction</div>', unsafe_allow_html=True)
    with st.form("expense_form"):
        c1, c2 = st.columns(2)
        with c1:
            description = st.text_input("Description", placeholder="e.g., Lunch with friends")
        with c2:
            amount = st.text_input("Amount", placeholder="e.g., 25.50")
        c3, c4, c5 = st.columns([1,1,1.2])
        with c3:
            expense_type = st.selectbox("Type", ["Expense", "Income"])
        with c4:
            category = st.selectbox("Category", ["Food", "Rent", "Utilities", "Salary", "Transport", "Marketing", "Misc"])
        with c5:
            expense_date = st.date_input("Date", value=date.today())
        submit = st.form_submit_button("Add Transaction")
        if submit:
            try:
                amt = float(amount)
                cursor.execute("""
                    INSERT INTO expenses (date, category, expense_type, amount, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (expense_date, category, expense_type, amt, description))
                conn.commit()
                st.success("Transaction added successfully.")
            except Exception as e:
                st.error(f"Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Upload CSV Card ---
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📎 Upload Expenses from CSV</div>', unsafe_allow_html=True)
    sample_csv = pd.DataFrame({
        "date": ["2025-07-01"],
        "category": ["Marketing"],
        "expense_type": ["Expense"],
        "amount": [5000],
        "description": ["Social Media Campaign"]
    })
    with st.expander("View Sample Format"):
        st.dataframe(sample_csv, use_container_width=True)
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file:
        try:
            df_upload = pd.read_csv(uploaded_file)
            df_upload["date"] = pd.to_datetime(df_upload["date"]).dt.date
            for _, row in df_upload.iterrows():
                cursor.execute("""
                    INSERT INTO expenses (date, category, expense_type, amount, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, tuple(row))
            conn.commit()
            st.success("Expenses uploaded successfully.")
        except Exception as e:
            st.error(f"Error uploading file: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Recent Transactions Card ---
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Recent Transactions</div>', unsafe_allow_html=True)
    try:
        df = pd.read_sql("SELECT date, category, expense_type, amount, description FROM expenses ORDER BY date DESC LIMIT 3", conn)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.info("No recent transactions found or error loading data.")
    st.markdown('<p style="font-size:0.95rem; color:#475569;">Note: Data is stored in your database.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Expense Summary Card ---
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Expense History & Summary</div>', unsafe_allow_html=True)
    try:
        df_all = pd.read_sql("SELECT date, category, expense_type, amount, description FROM expenses ORDER BY date DESC", conn)
        df_all["date"] = pd.to_datetime(df_all["date"]).dt.date
        # Summary Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Expenses", f"₹ {df_all[df_all['expense_type']=='Expense']['amount'].sum():,.2f}")
        col2.metric("Total Income", f"₹ {df_all[df_all['expense_type']=='Income']['amount'].sum():,.2f}")
        col3.metric("Transaction Count", f"{len(df_all):,}")
        # Bar Chart of Monthly Transactions
        df_all["month"] = pd.to_datetime(df_all["date"]).dt.to_period("M").astype(str)
        monthly_chart = df_all.groupby(["month", "expense_type"])["amount"].sum().reset_index()
        fig = px.bar(
            monthly_chart,
            x="month",
            y="amount",
            color="expense_type",
            barmode="group",
            title="Monthly Transaction Trend",
            text_auto='.2s'
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_color='#10284e',
            xaxis=dict(showgrid=False, title="Month"),
            yaxis=dict(showgrid=False, title="Amount (₹)"),
            legend_title_text="Transaction Type",
            title_font_size=19,
            margin=dict(l=30, r=30, t=60, b=30)
        )
        st.plotly_chart(fig, use_container_width=True)
        # Full Table
        with st.expander("Show All Transactions"):
            st.dataframe(df_all.drop(columns=['month']), use_container_width=True, hide_index=True)
    except Exception as e:
        st.info("No data or error loading summary.")
    st.markdown('</div>', unsafe_allow_html=True)
