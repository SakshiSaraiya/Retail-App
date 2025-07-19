import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Expense Dashboard", layout="wide")

# ✅ Text only color change (background stays white)
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            color: black !important;
            background-color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "expenses" not in st.session_state:
    data = {
        "date": ["2025-07-17", "2025-07-14"],
        "category": ["Rent", "Utilities"],
        "expense_type": ["Fixed", "Variable"],
        "amount": [10000, 3000],
        "description": ["Monthly rent", "Electricity bill"]
    }
    st.session_state.expenses = pd.DataFrame(data)

# ✅ 🔼 First Section: Add Expense
st.title("Add Expense")

with st.form("add_expense_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("Date", datetime.today())
    with col2:
        category = st.text_input("Category")
    with col3:
        expense_type = st.selectbox("Type", ["Fixed", "Variable"])

    amount = st.number_input("Amount", min_value=0.0, step=100.0)
    description = st.text_input("Description")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        new_row = pd.DataFrame({
            "date": [date],
            "category": [category],
            "expense_type": [expense_type],
            "amount": [amount],
            "description": [description]
        })
        st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
        st.success("Expense added!")

# ✅ 🔼 Second Section: Upload CSV
st.subheader("Upload CSV File")

with st.expander("View Sample Format"):
    st.markdown("Your file must contain: `date`, `category`, `expense_type`, `amount`, `description`")

uploaded = st.file_uploader("Upload CSV", type=["csv"])
if uploaded:
    try:
        new_data = pd.read_csv(uploaded)
        required_cols = {"date", "category", "expense_type", "amount", "description"}
        if required_cols.issubset(new_data.columns):
            st.session_state.expenses = pd.concat([st.session_state.expenses, new_data], ignore_index=True)
            st.success("File uploaded and merged successfully!")
        else:
            st.error("CSV missing required columns.")
    except Exception as e:
        st.error(f"Upload error: {e}")

# ✅ 🔽 Third Section: Expense History and Chart
df = st.session_state.expenses
st.title("Expense History and Trend")
st.dataframe(df, use_container_width=True)

st.subheader("Summary")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Expense", f"₹ {df['amount'].sum():,.2f}")
with col2:
    st.metric("Fixed Cost", f"₹ {df[df['expense_type'] == 'Fixed']['amount'].sum():,.2f}")
with col3:
    st.metric("Variable Cost", f"₹ {df[df['expense_type'] == 'Variable']['amount'].sum():,.2f}")

st.subheader("Monthly Expense Trend")

df["date"] = pd.to_datetime(df["date"])
df["Month"] = df["date"].dt.to_period("M").astype(str)

fig = px.bar(
    df,
    x="Month",
    y="amount",
    color="expense_type",
    barmode="group",
    labels={"amount": "Expense Amount", "Month": "Month"},
    color_discrete_sequence=px.colors.qualitative.Plotly
)

fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Expense Amount (₹)",
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color="black"),
    showlegend=True
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)

st.plotly_chart(fig, use_container_width=True)
