import streamlit as st
import base64

# --- Page Config ---
st.set_page_config(
    page_title="Home | Retail Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling ---
st.markdown("""
    <style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1E293B;
    }

    /* Sidebar text */
    section[data-testid="stSidebar"] .css-1d391kg, 
    section[data-testid="stSidebar"] .css-1v3fvcr, 
    section[data-testid="stSidebar"] .css-qri22k {
        color: white !important;
    }

    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 1rem;
    }

    /* Feature Cards */
    .feature-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
        height: 100%;
    }

    /* Headings */
    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-top: 2rem;
    }

    .feature-title {
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.4rem;
    }

    .platform-list li {
        padding: 0.2rem 0;
        font-size: 0.95rem;
    }

    /* Hide default Streamlit header */
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Content ---
st.markdown("<h1 style='font-weight:800;'>Welcome to All-in-One Retail Management</h1>", unsafe_allow_html=True)
st.markdown("Your centralized platform for inventory, finance, and vendor performance insights.")

# --- Key Features Section ---
st.markdown("<div class='section-title'>Key Features</div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
        <div class='feature-card'>
            <div class='feature-title'>Inventory Overview</div>
            <div>Monitor stock levels and categorize efficiently.</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class='feature-card'>
            <div class='feature-title'>Sales Highlights</div>
            <div>Track product trends, sales patterns, and profitability.</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
        <div class='feature-card'>
            <div class='feature-title'>Smart Inventory Suggestions</div>
            <div>Automate reorder points and reduce stockouts.</div>
        </div>
    """, unsafe_allow_html=True)

# --- Quick Access Section ---
st.markdown("<div class='section-title'>Quick Access</div>", unsafe_allow_html=True)
col4, col5 = st.columns(2)
with col4:
    st.markdown("""
        <div class='feature-card'>
            <div class='feature-title'>View Sales Dashboard</div>
            <div>Analyze revenue, forecasts, and category profitability.</div>
        </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown("""
        <div class='feature-card'>
            <div class='feature-title'>Manage Expenses</div>
            <div>Track fixed and variable costs for better financial control.</div>
        </div>
    """, unsafe_allow_html=True)

# --- Capabilities Section ---
st.markdown("<div class='section-title'>Platform Capabilities</div>", unsafe_allow_html=True)
st.markdown("""
<ul class='platform-list'>
    <li><b>Inventory Management</b> - Get stock alerts and movement reports</li>
    <li><b>Sales Analytics & Forecasting</b> - Product-wise, category-wise insights</li>
    <li><b>Vendor & Purchase Tracking</b> - Cost control and supplier scorecards</li>
    <li><b>Real-Time Financial Dashboards</b> - Profitability, cash flow, margins</li>
    <li><b>Expense Management</b> - Fixed vs variable cost control</li>
</ul>
""", unsafe_allow_html=True)
