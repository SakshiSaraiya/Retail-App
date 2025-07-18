import streamlit as st
import base64

# --- Page config ---
st.set_page_config(
    page_title="All-in-One Retail Management",
    layout="wide"
)

# --- Custom CSS Styling ---
custom_css = """
<style>
/* App background */
body, .stApp {
    background-color: #f4f6f9;
    font-family: 'Segoe UI', sans-serif;
    color: #222222;
}

/* Sidebar styling */
section[data-testid="stSidebar"] > div:first-child {
    background-color: #ffffff;
    border-right: 1px solid #e0e0e0;
    padding-top: 2rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* Sidebar logo title */
.st-emotion-cache-1v0mbdj {
    font-size: 20px !important;
    font-weight: 600 !important;
    color: #1a1a1a !important;
    margin-top: 1rem;
}

/* Card layout */
.feature-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.06);
    transition: transform 0.2s;
    height: 100%;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.08);
}

.card-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #2a2a2a;
}

.card-desc {
    font-size: 14px;
    color: #666666;
}

.section-title {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #1a1a1a;
    border-bottom: 2px solid #0057b8;
    padding-bottom: 6px;
}

ul.custom-bullets li::marker {
    color: #0057b8;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# --- Page Title ---
st.title("Welcome to All-in-One Retail Management")

# --- Key Features ---
st.markdown("<div class='section-title'>Key Features</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='feature-card'>
        <div class='card-title'>Inventory Overview</div>
        <div class='card-desc'>Monitor stock levels and categorize efficiently.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='feature-card'>
        <div class='card-title'>Sales Highlights</div>
        <div class='card-desc'>Track product trends, sales patterns, and profitability.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='feature-card'>
        <div class='card-title'>Smart Inventory Suggestions</div>
        <div class='card-desc'>Automate reorder points and reduce stockouts.</div>
    </div>
    """, unsafe_allow_html=True)

# --- Platform Capabilities ---
st.markdown("<div class='section-title'>Platform Capabilities</div>", unsafe_allow_html=True)

st.markdown("""
<ul class='custom-bullets'>
    <li><b>Inventory Management</b></li>
    <li><b>Sales Analytics and Forecasting</b></li>
    <li><b>Purchase Tracking and Vendor Insights</b></li>
    <li><b>Real-Time Financial Dashboards</b></li>
    <li><b>Expense Management & Profitability Analysis</b></li>
</ul>
""", unsafe_allow_html=True)
