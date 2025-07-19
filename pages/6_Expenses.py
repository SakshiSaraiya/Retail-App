import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from db_connector import get_connection

st.set_page_config(page_title="💸 Expenses", layout="wide")
st.title("Expense Management")

conn = get_connection()

# ----------------------------------
# Expense Input Form (Light Card Style)
# ----------------------------------
st.subheader("Add Expenses")
with st.container(border=True):
    with st.form("add_expense_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("Date", value=datetime.today())
        with col2:
            category = st.text_input("Category")
        with col3:
            expense_type = st.selectbox("Expense Type", ["Fixed", "Variable"])

        amount = st.number_input("Amount", min_value=0.0, step=100.0)
        description = st.text_input("Description")
        submitted = st.form_submit_button("Add Expense")

        if submitted:
            query = """
                INSERT INTO expenses (date, category, expense_type, amount, description)
                VALUES (%s, %s, %s, %s, %s)
            """
            conn.execute(query, (date, category, expense_type, amount, description))
            conn.commit()
            st.success("Expense added successfully.")

# ----------------------------------
# Upload Expenses from CSV
# ----------------------------------
st.subheader("Upload Expenses from CSV")
with st.expander("View Sample Format"):
    st.markdown("""**CSV Columns**: `date`, `category`, `expense_type`, `amount`, `description`
    
    **Example**:
    ```csv
    2025-07-01,Rent,Fixed,10000,Office Rent
    2025-07-02,Utilities,Variable,2000,Electricity
    ```
    """)

uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
if uploaded_file is not None:
    try:
        df_upload = pd.read_csv(uploaded_file)
        df_upload.to_sql("expenses", conn, if_exists="append", index=False)
        st.success("Expenses uploaded successfully.")
    except Exception as e:
        st.error(f"Error: {e}")

# ----------------------------------
# Expense History & Summary
# ----------------------------------
st.subheader("Expense History & Summary")
expenses_df = pd.read_sql("SELECT * FROM expenses ORDER BY date DESC", conn)
st.dataframe(expenses_df, use_container_width=True, hide_index=True)

# Totals Summary
total_expense = expenses_df["amount"].sum()
fixed_total = expenses_df[expenses_df["expense_type"] == "Fixed"]["amount"].sum()
variable_total = expenses_df[expenses_df["expense_type"] == "Variable"]["amount"].sum()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Expenses", f"₹ {total_expense:,.2f}")
with col2:
    st.metric("Fixed Costs", f"₹ {fixed_total:,.2f}")
with col3:
    st.metric("Variable Costs", f"₹ {variable_total:,.2f}")

# ----------------------------------
# Monthly Expense Trend
# ----------------------------------
st.subheader("Monthly Expense Trend")
expenses_df["month"] = pd.to_datetime(expenses_df["date"]).dt.to_period("M").astype(str)
monthly_expenses = expenses_df.groupby(["month", "expense_type"]).agg({"amount": "sum"}).reset_index()

fig = px.bar(
    monthly_expenses,
    x="month",
    y="amount",
    color="expense_type",
    barmode="group",
    text_auto=".2s",
    title="Monthly Expense by Type"
)
fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Amount (₹)",
    legend_title="Expense Type",
    font=dict(size=14),
    title_font=dict(size=18),
    plot_bgcolor="#fff",
    paper_bgcolor="#fff"
)
fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True)
