import streamlit as st

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
        background-color: #0F172A;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    .block-container {
        background-color: #F8FAFC;
        padding-top: 2rem;
    }

    /* Heading and Subheading */
    h1 {
        color: #0F172A !important;
        font-weight: 900;
        font-size: 2.4rem !important;
        margin-bottom: 0.4rem;
    }

    .subheading {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 2rem;
    }

    /* Cards */
    .feature-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        color: #1E293B;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 180px;
    }

    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1E293B;
        margin: 2rem 0 1rem;
    }

    .platform-list li {
        padding: 0.3rem 0;
        font-size: 0.95rem;
        color: #334155;
    }

    .stButton>button {
        background-color: #0F172A !important;
        color: white !important;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
    }

    .stButton>button:hover {
        background-color: #1E293B !important;
    }

    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<h1>Welcome to All-in-One Retail Management</h1>", unsafe_allow_html=True)
st.markdown("<div class='subheading'>Your centralized platform for inventory, finance, and vendor performance insights.</div>", unsafe_allow_html=True)

# --- Key Features ---
st.markdown("<div class='section-title'>Key Features</div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
        <div class='feature-card'>
            <h4>Inventory Overview</h4>
            <p>Monitor stock levels, categories, and reorder thresholds.</p>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class='feature-card'>
            <h4>Sales Highlights</h4>
            <p>Visualize revenue, spot trends, and assess category performance.</p>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
        <div class='feature-card'>
            <h4>Smart Inventory Suggestions</h4>
            <p>Leverage automated restocking alerts and demand forecasting.</p>
        </div>
    """, unsafe_allow_html=True)

# --- Quick Access using st.page_link ---
st.markdown("<div class='section-title'>Quick Access</div>", unsafe_allow_html=True)
col4, col5 = st.columns(2)

with col4:
    st.markdown("""
        <div class='feature-card'>
            <h4>Upload New Data</h4>
            <p>Quickly upload product, purchase, or sales records.</p>
        </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/0_upload_data.py", label="Go to Upload Page")

with col5:
    st.markdown("""
        <div class='feature-card'>
            <h4>View Financial Dashboard</h4>
            <p>Analyze revenue, expenses, and overall business health.</p>
        </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/5_Finance_Dashboard.py", label="Go to Financial Dashboard")

# --- Platform Capabilities ---
st.markdown("<div class='section-title'>Platform Capabilities</div>", unsafe_allow_html=True)
st.markdown("""
<ul class='platform-list'>
    <li><b>Inventory Management</b> – Track stock, suppliers, and reorder levels.</li>
    <li><b>Sales Analytics</b> – Understand product demand, trends, and profitability.</li>
    <li><b>Purchase Monitoring</b> – Control procurement and vendor performance.</li>
    <li><b>Financial Dashboards</b> – Gain real-time insights into margins and cash flow.</li>
    <li><b>Expense Control</b> – Monitor costs and improve budgeting decisions.</li>
</ul>
""", unsafe_allow_html=True)
