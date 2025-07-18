import streamlit as st
from streamlit_extras.colored_header import colored_header
import datetime

# -------------------------
# App Config
# -------------------------
st.set_page_config(
    page_title="All-in-One Retail Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# Sidebar Styling
# -------------------------
with st.sidebar:
    st.markdown("""
        <style>
        .css-1d391kg, .css-1cpxqw2, .css-ffhzg2 {
            color: white !important;
            background-color: #0D1B2A !important;
        }
        .css-6qob1r:hover {
            background-color: #1B263B !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.title("📦 All-in-One Retail")
    st.markdown("""---""")
    st.markdown("""
        <style>
        .css-1v3fvcr { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

# -------------------------
# Page Heading
# -------------------------
today = datetime.datetime.now().strftime("%A %d %B, %Y")
st.markdown(f"<h2 style='font-size:2.5rem; font-weight:700;'>Welcome to All-in-One Retail Management</h2>", unsafe_allow_html=True)
st.markdown(f"<h6 style='color:gray;'>{today}</h6>", unsafe_allow_html=True)

# -------------------------
# Intro Banner Section
# -------------------------
colored_header("Key Features", description=None, color_name="blue-70")
st.markdown("""
<div style='display: flex; gap: 1.5rem;'>
    <div style='flex: 1; background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 8px rgba(0,0,0,0.05);'>
        <h5 style='font-weight:600;'>Inventory Overview</h5>
        <p style='color:#444;'>Monitor stock levels and categorize efficiently.</p>
    </div>
    <div style='flex: 1; background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 8px rgba(0,0,0,0.05);'>
        <h5 style='font-weight:600;'>Sales Highlights</h5>
        <p style='color:#444;'>Track product trends, sales patterns, and profitability.</p>
    </div>
    <div style='flex: 1; background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 8px rgba(0,0,0,0.05);'>
        <h5 style='font-weight:600;'>Smart Inventory Suggestions</h5>
        <p style='color:#444;'>Automate reorder points and reduce stockouts.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------
# Platform Capabilities Section
# -------------------------
colored_header("Platform Capabilities", description=None, color_name="blue-70")
st.markdown("""
- **Inventory Management**
- **Sales Analytics and Forecasting**
- **Purchase Tracking and Vendor Insights**
- **Real-Time Financial Dashboards**
- **Expense Management & Profitability Analysis**
""")

# -------------------------
# Optional Additional Section
# -------------------------
# st.markdown("""
# ### What's New
# - Version 1.2 released with enhanced analytics and pricing simulator.
# - UI revamp for smoother user experience.
# """)

# -------------------------
# Hide Streamlit Footer
# -------------------------
st.markdown("""
    <style>
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
