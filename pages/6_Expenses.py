import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Expense Dashboard", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        .css-1v3fvcr, .css-1v0mbdj { color: #111 !important; }
        .stTextInput > div > div > input, .stSelectbox > div > div, .stDateInput > div > div > input {
            color: black !important;
        }
        .stButton > button {
            background-color: #4a4aff;
            color: white;
            font-weight: bold;
        }
        .stButton > button:hover {
            background-color: #3333cc;
        }
        .summary-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Expense History & Trends")

# Upload/initial data
if "expenses" not in st.session_state:
    data = {
        "date": ["2025-07-17", "2025-07-14"],
        "category": ["Rent", "Utilities"],
        "expense_type": ["Fixed", "Variable"],
        "amount": [10000, 3000],
        "description": ["Monthly rent", "Electricity bill"]
    }
    st.session_state.expenses = pd.DataFrame(data)

df = st.session_state.expenses

st.dataframe(df, use_container_width=True)

st.subheader("Summary")

# Summary cards
total_expense = df["amount"].sum()
fixed = df[df["expense_type"] == "Fixed"]["amount"].sum()
variable = df[df["expense_type"] == "Variable"]["amount"].sum()

cols = st.columns(3)
for i, (title, value) in enumerate([("Total Expenses", total_expense), ("Fixed Costs", fixed), ("Variable Costs", variable)]):
    with cols[i]:
        st.markdown(f"""
            <div class="summary-card">
                <h4>{title}</h4>
                <h3>₹ {value:,.2f}</h3>
            </div>
        """, unsafe_allow_html=True)

# Monthly bar chart
st.subheader("Monthly Expense Trend")
df["date"] = pd.to_datetime(df["date"])
df["Month"] = df["date"].dt.to_period("M").astype(str)

bar_fig = px.bar(
    df,
    x="Month",
    y="amount",
    color="expense_type",
    barmode="group",
    title="",
    labels={"amount": "Expense Amount (₹)", "Month": "Month"},
    color_discrete_sequence=["#4a4aff", "#8888ff"]
)

bar_fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Expense Amount (₹)",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color="black"),
    showlegend=True
)
bar_fig.update_xaxes(showgrid=False)
bar_fig.update_yaxes(showgrid=False)

st.plotly_chart(bar_fig, use_container_width=True)

# Add new expense
st.markdown("---")
st.title("📝 Expense Management")
st.subheader("Add a New Expense")

with st.form("add_expense_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("Date", datetime.today())
    with col2:
        category = st.text_input("Category")
    with col3:
        expense_type = st.selectbox("Type", ["Fixed", "Variable"])

    amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
    description = st.text_input("Description")
    submitted = st.form_submit_button("➕ Add Expense")

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

# Upload CSV section
st.subheader("Upload Expenses from CSV")
with st.expander("📎 View Sample Format"):
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
