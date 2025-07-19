import streamlit as st
import pandas as pd
from db_connector import get_connection
from datetime import date
import plotly.express as px

# Inject CSS for professional theme
with open("professional_theme.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Page Config ---
st.set_page_config(page_title="Expense Management", layout="wide")

# --- Title ---
st.markdown("<h1 style='color:#0F172A;'>Expense Management</h1>", unsafe_allow_html=True)

conn = get_connection()
cursor = conn.cursor()

# --------- Expense Entry Form ---------
st.markdown("<h3 style='color:#0F172A;'>Add a New Expense</h3>", unsafe_allow_html=True)

with st.expander("➕ Add Expense Form", expanded=False):
    with st.form("expense_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            expense_date = st.date_input("Expense Date", value=date.today())
        with col2:
            category = st.selectbox("Category", ["Rent", "Salary", "Utilities", "Marketing", "Transport", "Misc"])
        with col3:
            expense_type = st.selectbox("Type", ["Fixed", "Variable"])

        amount = st.number_input("Amount (\u20B9)", min_value=0.0, format="%.2f")
        description = st.text_input("Optional Description")

        submit = st.form_submit_button("Add Expense")

        if submit:
            try:
                cursor.execute("""
                    INSERT INTO expenses (date, category, expense_type, amount, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (expense_date, category, expense_type, amount, description))
                conn.commit()
                st.success("Expense added successfully.")
            except Exception as e:
                st.error(f"Error: {e}")

# --------- CSV Upload ---------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#0F172A;'>Upload Expenses from CSV</h3>", unsafe_allow_html=True)

sample_csv = pd.DataFrame({
    "date": ["2025-07-01"],
    "category": ["Marketing"],
    "expense_type": ["Variable"],
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

# --------- Expense History & Summary ---------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#0F172A;'>Expense History & Trends</h3>", unsafe_allow_html=True)

try:
    df = pd.read_sql("SELECT date, category, expense_type, amount, description FROM expenses ORDER BY date DESC", conn)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    st.dataframe(df, use_container_width=True)

    st.markdown("<h4 style='color:#0F172A;'>Summary</h4>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Expenses", f"₹ {df['amount'].sum():,.2f}")
    col2.metric("Fixed Costs", f"₹ {df[df['expense_type']=='Fixed']['amount'].sum():,.2f}")
    col3.metric("Variable Costs", f"₹ {df[df['expense_type']=='Variable']['amount'].sum():,.2f}")

    # Monthly Trend
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    monthly_chart = df.groupby(["month", "expense_type"])["amount"].sum().reset_index()

    fig = px.bar(monthly_chart, x="month", y="amount", color="expense_type",
                 title="Monthly Expense Trend", barmode="group",
                 color_discrete_sequence=["#1E293B", "#64748B"])
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.warning("No expense records found or database error.")
