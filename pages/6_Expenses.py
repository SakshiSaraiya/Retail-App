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

# --- CSS Styling ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }

    [data-testid="stSidebar"] .css-1d391kg,
    [data-testid="stSidebar"] .css-1v3fvcr,
    [data-testid="stSidebar"] .css-qri22k {
        color: #F1F5F9 !important;
    }

    .block-container {
        background-color: #F9FAFB;
        padding-top: 2rem;
    }

    h1, h3 {
        color: #1E293B !important;
        font-weight: 700;
    }

    .stButton > button {
        background-color: #1E40AF;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        transition: 0.3s;
    }

    .stButton > button:hover {
        background-color: #1D4ED8;
        transform: scale(1.02);
    }

    .stDataFrame div {
        font-size: 0.95rem;
        padding: 4px;
    }

    .metric-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        text-align: center;
    }

    .metric-card h2 {
        font-size: 1.25rem;
        color: #475569;
    }

    .metric-card p {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1E293B;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h1>Expense Management</h1>", unsafe_allow_html=True)

conn = get_connection()
cursor = conn.cursor()

# --------- Expense Entry Form ---------
st.markdown("<h3>Add a New Expense</h3>", unsafe_allow_html=True)

with st.expander("➕ Add Expense Form", expanded=False):
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

# --------- CSV Upload ---------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3>Upload Expenses from CSV</h3>", unsafe_allow_html=True)

sample_csv = pd.DataFrame({
    "date": ["2025-07-01"],
    "category": ["Marketing"],
    "expense_type": ["Variable"],
    "amount": [5000],
    "description": ["Social Media Campaign"]
})
with st.expander("📎 View Sample Format"):
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
st.markdown("<h3>Expense History & Trends</h3>", unsafe_allow_html=True)

try:
    df = pd.read_sql("SELECT date, category, expense_type, amount, description FROM expenses ORDER BY date DESC", conn)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    st.dataframe(df, use_container_width=True)

    st.markdown("### Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <h2>Total Expenses</h2>
                <p>₹ {df['amount'].sum():,.2f}</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <h2>Fixed Costs</h2>
                <p>₹ {df[df['expense_type']=='Fixed']['amount'].sum():,.2f}</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <h2>Variable Costs</h2>
                <p>₹ {df[df['expense_type']=='Variable']['amount'].sum():,.2f}</p>
            </div>
        """, unsafe_allow_html=True)

    # Monthly Trend
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    monthly_chart = df.groupby(["month", "expense_type"])["amount"].sum().reset_index()

    fig = px.bar(
        monthly_chart, 
        x="month", 
        y="amount", 
        color="expense_type",
        barmode="group",
        title="Monthly Expense Trend",
        color_discrete_sequence=["#6366F1", "#60A5FA"]
    )

    fig.update_traces(marker_line_width=0.5, marker_line_color="rgba(0,0,0,0.1)")
    fig.update_layout(
        plot_bgcolor="#F9FAFB",
        paper_bgcolor="#F9FAFB",
        font=dict(color="#1E293B", size=14),
        title_font=dict(size=20, color="#1E293B", family="Arial"),
        xaxis_title="Month",
        yaxis_title="Expense Amount (₹)",
        legend_title_text='Type',
        bargap=0.15,
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.warning("No expense records found or database error.")
