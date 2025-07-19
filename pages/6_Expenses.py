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

# --- Custom CSS Styling ---
st.markdown("""
    <style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }
    [data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }

    /* Main page background */
    .block-container {
        background-color: #FFFFFF;
        padding-top: 2rem;
    }

    /* Headings and text */
    h1, h2, h3, h4, h5, h6, label, p, li, span, div {
        color: #0F172A !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #0F172A;
        color: white;
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton > button:hover {
        background-color: #1E293B;
    }

    /* Dataframe text */
    .stDataFrame div {
        color: #111827 !important;
    }

    /* Card-like metric containers */
    .metric-card {
        background-color: #F1F5F9;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        text-align: center;
        font-weight: 600;
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h1>Expense Management</h1>", unsafe_allow_html=True)

# --- DB Connection ---
conn = get_connection()
cursor = conn.cursor()

# --------- Add Manually Section ---------
st.markdown("### Add Expenses")

if st.button("➕ Add Manually"):
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

# --------- CSV Upload Section ---------
st.markdown("### 📎 Upload Expenses from CSV")

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
st.markdown("### 📊 Expense History & Summary")

try:
    df = pd.read_sql("SELECT date, category, expense_type, amount, description FROM expenses ORDER BY date DESC", conn)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    st.dataframe(df, use_container_width=True)

    # Metric cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class='metric-card'>Total Expenses<br><strong>₹ {df['amount'].sum():,.2f}</strong></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='metric-card'>Fixed Costs<br><strong>₹ {df[df['expense_type']=='Fixed']['amount'].sum():,.2f}</strong></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class='metric-card'>Variable Costs<br><strong>₹ {df[df['expense_type']=='Variable']['amount'].sum():,.2f}</strong></div>""", unsafe_allow_html=True)

    # --- Monthly Bar Chart ---
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    monthly_chart = df.groupby(["month", "expense_type"])["amount"].sum().reset_index()

    fig = px.bar(
        monthly_chart,
        x="month",
        y="amount",
        color="expense_type",
        title="Monthly Expense Trend",
        barmode="group",
        text_auto='.2s',
        color_discrete_sequence=["#1E3A8A", "#60A5FA"]
    )

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='#0F172A',
        title_font_size=18,
        xaxis=dict(showgrid=False, title="Month", color="#0F172A"),
        yaxis=dict(showgrid=False, title="Amount (₹)", color="#0F172A"),
        legend_title=dict(text="Expense Type", font=dict(color="#0F172A"))
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.warning(f"No data or error loading data: {e}")
