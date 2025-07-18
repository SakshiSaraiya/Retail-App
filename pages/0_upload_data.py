import streamlit as st
import pandas as pd
from db_connector import get_connection

# --- Page Config ---
st.set_page_config(
    page_title="Upload Data | Retail Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }

    .block-container {
        background-color: #F8FAFC;
        padding-top: 2rem;
        color: #1E293B;
    }

    h1 {
        color: #0F172A !important;
        font-weight: 800;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1E293B;
        margin: 2rem 0 1rem;
    }

    .stFileUploader label, .stTextInput label, .stNumberInput label,
    .stSelectbox label, .stDateInput label {
        font-weight: 600;
        color: #334155;
    }

    .stButton>button {
        background-color: #0F172A;
        color: white;
        font-weight: 600;
        border-radius: 8px;
    }

    .stButton>button:hover {
        background-color: #1E293B;
        color: white;
    }

    .stExpanderHeader {
        font-weight: 600;
        color: #1E293B;
    }

    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h1>Upload or Add Inventory Data</h1>", unsafe_allow_html=True)

# --- Database Connection ---
conn = get_connection()
if conn is None:
    st.stop()

cursor = conn.cursor()

# --- Upload Section ---
st.markdown("<div class='section-title'>Upload CSV Files</div>", unsafe_allow_html=True)

# PRODUCT UPLOAD
product_file = st.file_uploader("Upload Product CSV", type=["csv"])
if product_file:
    df = pd.read_csv(product_file)
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO product (product_id, product_name, category, stock)
                VALUES (%s, %s, %s, %s)
            """, (row['product_id'], row['product_name'], row['category'], row['stock']))
        except Exception as e:
            st.warning(f"Skipped a row due to error: {e}")
    conn.commit()
    st.success("Product data uploaded successfully!")

# PURCHASE UPLOAD
purchase_file = st.file_uploader("Upload Purchase CSV", type=["csv"])
if purchase_file:
    df = pd.read_csv(purchase_file)
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO purchases (product_id, product_name,
