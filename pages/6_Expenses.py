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

# --- Custom Styling ---
st.markdown("""
    <style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }
    [data-testid="stSidebar"] * {
        color: #F1F5F9 !important;
    }

    /* Main background */
    .block-container {
        background-color: #FFF8FAFC;
        padding: 2rem;
    }

    /* Headings and text */
    h1, h2, h3, label, p, .stText, .stMarkdown, div {
        color: #0F172A !important;
    }

    /* Input widgets */
    .stTextInput, .stNumberInput, .stDateInput, .stSelectbox, .stTextArea, .stFileUploader, .stDataFrame {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }

    input, textarea, select {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        padding: 0.5rem;
    }

    /* Metric Cards */
    .metric-card {
        background-color: #F8FAFC;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }

    /* Add Button */
    .add-expense-btn {
        background-color: #F8FAFC;
        color: #0F172A;
        font-weight: 600;
        border: 2px solid #0F172A;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-size: 1.5rem;
        cursor: pointer;
        transition: background-color 0.3s ease;
        margin-bottom: 1rem;
    }
    .add-expense-btn:hover {
        background-color: #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Page Title ---
st.markdown("<h1>Expense Management</h1>", unsafe_allow_html=True)

# --- DB Connection ---
conn = get_connection()
cursor = conn.cursor()

# --- Add Expenses Section ---
# Header and Add Button in a single row
header_col1, header_col2 = st.columns([0.85, 0.15])
with header_col1:
    st.markdown("### Add Expenses")
with header_col2:
    add_clicked = st.button("➕ Add Expense", key="add_expense_button", help="Click to add an expense")


if add_clicked or st.session_state.get("show_form", False):
    st.session_state["show_form"] = True  # Keep form visible once triggered

if st.session_state.get("show_form", False):
    with st.form("expense_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            expense_date = st.date_input("Expense Date", value=date.today())
        with col2:
            category = st.selectbox("Category", ["Rent", "Salary", "Utilities", "Marketing", "Transport", "Misc"])
        with col3:
            expense_type = st.selectbox("Type", ["Fixed", "Variable"])

        amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
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

# --- Upload from CSV ---
st.markdown("### Upload Expenses from CSV")

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

# --- Expense History & Summary ---
st.markdown("### Expense History & Summary")

try:
    df = pd.read_sql("SELECT date, category, expense_type, amount, description FROM expenses ORDER BY date DESC", conn)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    st.dataframe(df, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><h3>Total Expenses</h3><h2>₹ {:,.2f}</h2></div>'.format(df['amount'].sum()), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h3>Fixed Costs</h3><h2>₹ {:,.2f}</h2></div>'.format(df[df['expense_type']=='Fixed']['amount'].sum()), unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h3>Variable Costs</h3><h2>₹ {:,.2f}</h2></div>'.format(df[df['expense_type']=='Variable']['amount'].sum()), unsafe_allow_html=True)

    # --- Monthly Trend Chart ---
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    monthly_chart = df.groupby(["month", "expense_type"])["amount"].sum().reset_index()

    fig = px.bar(
        monthly_chart,
        x="month",
        y="amount",
        color="expense_type",
        barmode="group",
        text_auto='.2s'
    )

    fig.update_layout(
        title="Monthly Expense Trend",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='black',
        xaxis=dict(showgrid=False, title="Month", tickfont=dict(color='black')),
        yaxis=dict(showgrid=False, title="Amount (₹)", tickfont=dict(color='black')),
        legend_title_text="Expense Type",
        title_font=dict(color='black', size=18)
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.warning(f"No data or error loading data: {e}")
