import streamlit as st
import base64

st.set_page_config(
    page_title="Retail Management App",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS to darken sidebar and remove top black bar
st.markdown("""
    <style>
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #1F2937;
            color: white;
        }

        [data-testid="stSidebar"] .css-1v3fvcr, /* all nav items */
        [data-testid="stSidebar"] .css-1d391kg { 
            color: white !important;
        }

        /* Hide top black bar */
        header {visibility: hidden;}
        
        /* Remove borders and lines */
        hr {display: none;}

        /* Card style */
        .card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .card-title {
            font-weight: 600;
            font-size: 18px;
            color: #111827;
        }

        .card-body {
            color: #4B5563;
            font-size: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# Title block
st.markdown("""
    <h1 style='font-size: 38px; color: #111827; font-weight: 700;'>Welcome to All-in-One Retail Management</h1>
    <p style='font-size: 18px; color: #374151;'>Your centralized platform for inventory, finance, and vendor performance insights.</p>
    <br>
""", unsafe_allow_html=True)

# Key Feature Cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='card'>
        <div class='card-title'>Inventory Overview</div>
        <div class='card-body'>Monitor stock levels and categorize efficiently.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='card'>
        <div class='card-title'>Sales Highlights</div>
        <div class='card-body'>Track product trends, sales patterns, and profitability.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='card'>
        <div class='card-title'>Smart Inventory Suggestions</div>
        <div class='card-body'>Automate reorder points and reduce stockouts.</div>
    </div>
    """, unsafe_allow_html=True)

# Platform Capabilities section
st.markdown("""
    <h2 style='font-size: 26px; color: #111827; font-weight: 700;'>Platform Capabilities</h2>
    <ul style='font-size: 16px; color: #374151;'>
        <li><strong>Inventory Management</strong> - Get stock alerts and movement reports</li>
        <li><strong>Sales Analytics & Forecasting</strong> - Product-wise, category-wise insights</li>
        <li><strong>Vendor & Purchase Tracking</strong> - Cost control and supplier scorecards</li>
        <li><strong>Real-Time Financial Dashboards</strong> - Profitability, cash flow, margins</li>
        <li><strong>Expense Management</strong> - Fixed vs variable cost control</li>
    </ul>
""", unsafe_allow_html=True)

# Optional section: Summary cards or mini dashboard (optional visual touch)
col4, col5 = st.columns(2)
with col4:
    st.markdown("""
    <div class='card'>
        <div class='card-title'>Total Products Tracked</div>
        <div class='card-body'>Use the inventory and purchases section to track SKUs in real time.</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class='card'>
        <div class='card-title'>Real-Time Profit Monitoring</div>
        <div class='card-body'>View gross and net profit metrics under Finance Dashboard.</div>
    </div>
    """, unsafe_allow_html=True)
