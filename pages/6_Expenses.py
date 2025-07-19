import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ------------------ PAGE CONFIG + THEME FIX ------------------ #
st.set_page_config(page_title="Expense Management Dashboard", layout="wide")

# Force white background, black text, and styled inputs/buttons
st.markdown("""
    <style>
        .main {
            background-color: white !important;
        }
        body, html {
            background-color: white !important;
            color: black !important;
        }
        .stTextInput input, .stDateInput input, .stNumberInput input, .stSelectbox div {
            background-color: white !important;
            color: black !important;
        }
        .stButton>button {
            background-color: #1f77b4;
            color: white !important;
            border: none;
            border-radius: 6px;
        }
        .stButton>button:hover {
            background-color: #105c91;
        }
        .stDataFrame {
            color: black !important;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ SESSION STATE TO STORE EXPENSES ------------------ #
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Expense Type", "Amount", "Description"])

# ------------------ TITLE ------------------ #
st.title("Expense Management Dashboard")

# ------------------ MANUAL EXPENSE ENTRY ------------------ #
st.subheader("Add Expense Manually")

with st.form("manual_entry"):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("Date", datetime.today())
    with col2:
        category = st.text_input("Category")
    with col3:
        expense_type = st.selectbox("Expense Type", ["Fixed", "Variable"])

    amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01)
    description = st.text_input("Description")

    submitted = st.form_submit_button("Add Expense")
    if submitted:
        new_entry = pd.DataFrame([{
            "Date": date.strftime("%Y-%m-%d"),
            "Category": category,
            "Expense Type": expense_type,
            "Amount": amount,
            "Description": description
        }])
        st.session_state.expenses = pd.concat([st.session_state.expenses, new_entry], ignore_index=True)
        st.success("Expense added successfully.")

# ------------------ FILE UPLOAD SECTION ------------------ #
st.subheader("Upload Expenses via CSV")

with st.expander("📄 View Sample CSV Format"):
    st.markdown("Your CSV file should have the following columns:")
    st.code("Date, Category, Expense Type, Amount, Description", language="csv")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
if uploaded_file is not None:
    df_uploaded = pd.read_csv(uploaded_file)
    if set(["Date", "Category", "Expense Type", "Amount", "Description"]).issubset(df_uploaded.columns):
        st.session_state.expenses = pd.concat([st.session_state.expenses, df_uploaded], ignore_index=True)
        st.success("CSV uploaded and merged with existing data.")
    else:
        st.error("CSV must contain columns: Date, Category, Expense Type, Amount, Description")

# ------------------ DISPLAY EXPENSE HISTORY ------------------ #
st.subheader("Expense History and Trends")

if not st.session_state.expenses.empty:
    st.dataframe(st.session_state.expenses)

    # Bar chart of expenses by category
    fig = px.bar(
        st.session_state.expenses,
        x="Category",
        y="Amount",
        color="Expense Type",
        title="Expenses by Category",
        barmode="group",
        template="simple_white",
        labels={"Amount": "₹ Amount"}
    )
    fig.update_layout(
        xaxis_title="Category",
        yaxis_title="Amount (₹)",
        legend_title="Expense Type",
        title_font=dict(size=18),
        title_x=0.5
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No expenses to display. Add some manually or upload a CSV.")
