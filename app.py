import streamlit as st 
from streamlit_lottie import st_lottie
import requests
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="📊 Retail Dashboard",
    layout="wide"
)

# Load Lottie animations
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

inventory_lottie = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_jcikwtux.json")
retail_lottie = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_9cyyl8i4.json")

# --- Custom Background and CSS ---
st.markdown("""
    <style>
        .stApp {
            background-color: #F8F9FB;
        }
        [data-testid="stSidebar"] {
            background-color: #4527A0;
        }
        [data-testid="stSidebar"] .css-1v0mbdj {
            color: white;
        }
        h1, h2, h3, .stMarkdown p {
            color: #111827;
        }
        .info-card {
            background-color: #FFFFFF;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title Section ---
st.markdown("<h1 style='text-align:left;'>Welcome to <strong>Retail Compass</strong></h1>", unsafe_allow_html=True)
st.markdown(f"**📅 {datetime.today().strftime('%A %d %B, %Y')}**")
st.markdown("<hr>", unsafe_allow_html=True)

# --- Info Cards ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("📦 Inventory Overview")
    st.write("Monitor stock levels & categories.")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("⚡ Sales Highlights")
    st.write("Track trends, products & profits.")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("🧠 Smart Tip")
    st.write("Automate reordering to avoid stockouts.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main Layout ---
left_col, right_col = st.columns([1.3, 1])

with left_col:
    st.subheader("📋 Features")
    st.markdown("""
    - **Inventory:** Stock tracking & categorization.
    - **Sales:** Product trends & transactions.
    - **Purchases:** Vendor data & payment logs.
    """)

    st.subheader("🚀 How to Start")
    st.markdown("""
    1. Upload your inventory & sales data.
    2. Explore dashboards from the sidebar.
    3. Get insights on sales, inventory & profitability.
    """)

    st.subheader("🛠 Built With")
    st.markdown("- Python + Streamlit\n- MySQL\n- Plotly Dashboards")

    st.markdown("### 🔗 Quick Access")
    colA, colB = st.columns(2)
    with colA:
        if st.button("📤 Upload Data"):
            st.switch_page("pages/0_upload_data.py")
    with colB:
        if st.button("📊 View Dashboard"):
            st.switch_page("pages/1_Home.py")

with right_col:
    st_lottie(inventory_lottie, height=220, key="inventory_anim")
    st_lottie(retail_lottie, height=220, key="retail_anim")

# --- Footer ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center;'>
    🔒 Secure | ⚡ Fast | 🎯 Accurate<br>
    <span style='font-size:12px;'>Built by Sakshi Saraiya & Chirag Thakkar</span>
</div>
""", unsafe_allow_html=True)
