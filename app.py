import streamlit as st
from streamlit_lottie import st_lottie
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="Retail Compass",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Lottie Animations ---
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_animation = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_jcikwtux.json")

# --- Custom Styling ---
st.markdown("""
    <style>
        .stApp {
            background-color: #f5f6fa;
            color: #1f1f1f;
        }
        .sidebar .sidebar-content {
            background-color: #1f1f2e;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #1a1a1a;
        }
        .card {
            background-color: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            text-align: center;
        }
        .card-title {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .card-desc {
            font-size: 14px;
            color: #555;
        }
        .button-style button {
            background-color: #2b2d42;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
        }
        .button-style button:hover {
            background-color: #1f7aec;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("""
    <h1 style='text-align: center; font-size: 42px;'>Retail Compass</h1>
    <p style='text-align: center; font-size: 18px;'>A unified platform to manage inventory, sales, and finances efficiently.</p>
    <br>
""", unsafe_allow_html=True)

# --- Feature Overview ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class='card'>
        <div class='card-title'>Inventory Overview</div>
        <div class='card-desc'>Monitor stock levels & categorize efficiently.</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class='card'>
        <div class='card-title'>Sales Highlights</div>
        <div class='card-desc'>Track trends, products & profits with clarity.</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class='card'>
        <div class='card-title'>Smart Suggestions</div>
        <div class='card-desc'>Automate reorder points & avoid stockouts.</div>
    </div>
    """, unsafe_allow_html=True)

# --- Features List ---
st.subheader("Platform Capabilities")
st.markdown("""
- Inventory Management
- Sales Analysis and Forecasting
- Purchase & Vendor Tracking
- Financial Dashboards
- Expense Categorization and Reporting
""")

# --- Navigation Buttons ---
col1, col2 = st.columns(2)
with col1:
    if st.button("Upload Data", use_container_width=True):
        st.switch_page("pages/0_upload_data.py")
with col2:
    if st.button("View Inventory", use_container_width=True):
        st.switch_page("pages/1_Home.py")

# --- Animation ---
st_lottie(lottie_animation, height=280, key="main_anim")

# --- Footer ---
st.markdown("""
<hr>
<div style='text-align:center; font-size:13px;'>
    Built by Sakshi Saraiya & Chirag Thakkar | Secure • Fast • Insightful
</div>
""", unsafe_allow_html=True)
