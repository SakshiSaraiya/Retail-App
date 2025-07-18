import streamlit as st
from streamlit_lottie import st_lottie
import requests

# Config
st.set_page_config(
    page_title="Retail Compass",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Lottie Animations
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

retail_lottie = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_9cyyl8i4.json")

# Styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #f5f7fa, #e4ecf7);
        color: #1f2937;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3, h4 {
        color: #102a43;
        font-weight: 700;
    }
    .feature-card {
        background-color: #ffffff;
        padding: 1.75rem;
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
        text-align: left;
        transition: transform 0.2s ease;
        border: 1px solid #d9e2ec;
    }
    .feature-card:hover {
        transform: translateY(-3px);
    }
    .footer {
        text-align: center;
        font-size: 13px;
        color: #486581;
        margin-top: 40px;
    }
    .cta-button {
        margin-top: 12px;
    }
    .highlight-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    .highlight-text {
        font-size: 14px;
        color: #334e68;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h1 style='text-align:center;'>Retail Compass</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;font-size:18px;'>A unified platform to manage inventory, sales, and finances efficiently.</p>", unsafe_allow_html=True)

st.divider()

# --- Feature Highlights ---
st.markdown("### Key Features")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='feature-card'>
        <div class='highlight-title'>Inventory Overview</div>
        <div class='highlight-text'>Monitor stock levels and categorize efficiently.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='feature-card'>
        <div class='highlight-title'>Sales Highlights</div>
        <div class='highlight-text'>Track product trends, sales patterns, and profitability.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='feature-card'>
        <div class='highlight-title'>Smart Inventory Suggestions</div>
        <div class='highlight-text'>Automate reorder points and reduce stockouts.</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- Platform Capabilities & Lottie ---
left, right = st.columns([1.2, 1])

with left:
    st.markdown("### Platform Capabilities")
    st.markdown("""
    - Inventory Management  
    - Sales Analysis and Forecasting  
    - Purchase and Vendor Tracking  
    - Financial Dashboards  
    - Expense Categorization and Reporting  
    """)

    st.markdown("#### Quick Navigation")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Upload Data"):
            st.switch_page("pages/0_upload_data.py")
    with col_btn2:
        if st.button("View Inventory"):
            st.switch_page("pages/1_Home.py")

with right:
    if retail_lottie:
        st_lottie(retail_lottie, height=260)

# --- Footer ---
st.markdown("<div class='footer'>© 2025 Retail Compass — Developed by Sakshi Saraiya & Chirag Thakkar</div>", unsafe_allow_html=True)
