import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Set page config
st.set_page_config(page_title="Expense Manager", layout="wide")

# Initialize session state
if "expense_data" not in st.session_state:
    st.session_state.expense_data = pd.DataFrame(columns=["Date", "Category", "Expense Type", "Amount", "Description"])

if "show_form" not in st.session_state:
    st.session_state.show_form = False

# Apply custom CSS
st.markdown("""
    <style>
        .main {
            color: #000000 !important;
        }
        h1, h2, h3, h4 {
            color: #000000 !important;
        }
        .stButton>button {
            background-color: #1f77b4;
            color: white;
        }
        .stButton>button:hover {
            background-color: #105c91;
        }
        .css-1cpxqw2 {
            color: #000000 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("Expense Management Dashboard")

# --- Toggle for Add Expense Form ---
st.subheader("Add Expense Manually")
if st.button("Add Manually"):
    st.session_state.show_form = not st.session_state.show_form

# --- Add Expense Form ---
if st.session_state.show_form:
    with st.form("manual_expense_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            date_input = st.date_input("Date", value=date.today())
        with col2:
            category = st.text_input("Category")
        with col3:
            expense_type = st.selectbox("Expense Type", ["Fixed", "Variable"])
        amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01)
        description = st.text_input("Description")
        submit = st.form_submit_button("Add Expense")
        if submit:
            new_data = {
                "Date": pd.to_datetime(date_input),
                "Category": category,
                "Expense Type": expense_type,
                "Amount": amount,
                "Description": description
            }
            st.session_state.expense_data = pd.concat([st.session_state.expense_data, pd.DataFrame([new_data])], ignore_index=True)
            st.success("Expense added successfully!")

# --- Upload Expenses via CSV ---
st.subheader("Upload Expenses via CSV")
with st.expander("📄 View Sample CSV Format"):
    st.markdown("""
    **Sample Format:**  
    `Date`, `Category`, `Expense Type`, `Amount`, `Description`  
    `2025-07-01`, `Rent`, `Fixed`, `10000`, `Monthly rent`
    """)
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["Date"] = pd.to_datetime(df["Date"])
    st.session_state.expense_data = pd.concat([st.session_state.expense_data, df], ignore_index=True)
    st.success("CSV uploaded and data added!")

# --- Expense Table and Summary ---
st.subheader("Expense History and Trends")

if not st.session_state.expense_data.empty:
    # Expense table
    st.dataframe(st.session_state.expense_data.style.format({"Amount": "₹{:.2f}"}))

    # Summary
    total_expense = st.session_state.expense_data["Amount"].sum()
    fixed_expense = st.session_state.expense_data[st.session_state.expense_data["Expense Type"] == "Fixed"]["Amount"].sum()
    variable_expense = total_expense - fixed_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Expenses", f"₹ {total_expense:,.2f}")
    col2.metric("Fixed", f"₹ {fixed_expense:,.2f}")
    col3.metric("Variable", f"₹ {variable_expense:,.2f}")

    # Bar chart of expenses by type over time
    st.markdown("### Monthly Expense by Type")
    monthly_data = st.session_state.expense_data.copy()
    monthly_data["Month"] = monthly_data["Date"].dt.to_period("M").dt.to_timestamp()
    chart_data = monthly_data.groupby(["Month", "Expense Type"])["Amount"].sum().reset_index()

    fig = px.bar(
        chart_data,
        x="Month",
        y="Amount",
        color="Expense Type",
        barmode="group",
        title="Monthly Expense Comparison",
        labels={"Amount": "Amount (₹)"}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No expenses yet. Add manually or upload a CSV to begin.")
