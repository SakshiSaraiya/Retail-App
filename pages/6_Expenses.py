import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Expense Management", layout="wide")

# ✅ Custom CSS: Sidebar dark, main area white with black text
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #1c1c1c;
        }
        .block-container {
            background-color: white;
            color: black;
        }
        h1, h2, h3, h4, h5, h6 {
            color: black !important;
        }
        .stTextInput > div > div > input,
        .stNumberInput input,
        .stDateInput input,
        .stSelectbox div div {
            color: black !important;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ Session state to store expenses
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=[
        "date", "category", "expense_type", "amount", "description"
    ])

# ✅ Page Title
st.title("Expense Management Dashboard")

# ✅ Section 1: Add Expense Manually
st.header("Add Expense Manually")

with st.form("manual_expense_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("Date", datetime.today())
    with col2:
        category = st.text_input("Category")
    with col3:
        expense_type = st.selectbox("Expense Type", ["Fixed", "Variable"])

    amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
    description = st.text_input("Description")

    submit = st.form_submit_button("Add Expense")

    if submit:
        new_row = pd.DataFrame({
            "date": [date],
            "category": [category],
            "expense_type": [expense_type],
            "amount": [amount],
            "description": [description]
        })
        st.session_state.expenses = pd.concat(
            [st.session_state.expenses, new_row], ignore_index=True)
        st.success("Expense added successfully.")

# ✅ Section 2: Upload CSV File
st.header("Upload Expenses via CSV")

with st.expander("📄 View Sample CSV Format"):
    st.markdown("""
    Your CSV file should have the following columns:
    - `date`
    - `category`
    - `expense_type`
    - `amount`
    - `description`
    """)

uploaded = st.file_uploader("Upload CSV File", type="csv")
if uploaded:
    try:
        df_csv = pd.read_csv(uploaded)
        required_cols = {"date", "category", "expense_type", "amount", "description"}
        if required_cols.issubset(df_csv.columns):
            st.session_state.expenses = pd.concat(
                [st.session_state.expenses, df_csv], ignore_index=True)
            st.success("CSV file uploaded and merged.")
        else:
            st.error("Missing required columns in CSV.")
    except Exception as e:
        st.error(f"Error reading file: {e}")

# ✅ Section 3: Expense Summary and Chart
df = st.session_state.expenses.copy()
if not df.empty:
    st.header("Expense History and Trends")

    # Data Table
    st.subheader("Expense Table")
    st.dataframe(df, use_container_width=True)

    # Summary Metrics
    st.subheader("Expense Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Expense", f"₹ {df['amount'].sum():,.2f}")
    with col2:
        st.metric("Fixed", f"₹ {df[df['expense_type'] == 'Fixed']['amount'].sum():,.2f}")
    with col3:
        st.metric("Variable", f"₹ {df[df['expense_type'] == 'Variable']['amount'].sum():,.2f}")

    # Monthly Grouping for Chart
    df["date"] = pd.to_datetime(df["date"])
    df["Month"] = df["date"].dt.to_period("M").astype(str)

    # ✅ Clean Bar Chart (Professional Look)
    fig = px.bar(
        df,
        x="Month",
        y="amount",
        color="expense_type",
        barmode="group",
        labels={"amount": "Expense Amount (₹)", "Month": "Month"},
        color_discrete_sequence=px.colors.qualitative.Safe
    )

    fig.update_layout(
        title="Monthly Expense by Type",
        xaxis_title="Month",
        yaxis_title="Amount (₹)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="black"),
        showlegend=True
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No expense data available yet. Please add manually or upload a CSV.")
