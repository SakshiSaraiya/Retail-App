import streamlit as st

# --- Page Config ---
st.set_page_config(
    page_title="Home | Retail Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
    <style>
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }

    [data-testid="stSidebar"] .css-1d391kg,
    [data-testid="stSidebar"] .css-1v3fvcr,
    [data-testid="stSidebar"] .css-qri22k {
        color: #E2E8F0 !important;
    }

    /* Sidebar menu item hover */
    .css-1d391kg:hover {
        color: #38BDF8 !important;
    }

    /* Card Styling */
    .feature-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        height: 100%;
    }

    /* Title and Section Headers */
    h1, h2 {
        color: #0F172A;
        font-weight: 800;
    }

    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1E293B;
        margin: 2rem 0 1rem;
    }

    /* List Styling */
    .platform-list li {
        padding: 0.3rem 0;
        font-size: 0.95rem;
        color: #334155;
    }

    /* General Reset */
    header {visibility: hidden;}
    .block-container {padding-top: 2rem;}
    </style>
""", unsafe_allow_html=True)

# --- Welcome Section ---
st.markdown("<h1>Welcome to All-in-One Retail Management</h1>", unsafe_allow_html=True)
st.write("Your centralized platform for inventory, finance, and vendor performance insights.")

# --- Key Features Section ---
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

# --- Quick Access Section ---
st.markdown("<div class='section-title'>Quick Access</div>", unsafe_allow_html=True)
col4, col5 = st.columns(2)
with col4:
    st.markdown("""
        <div class='feature-card'>
            <h4>View Sales Dashboard</h4>
            <p>Drill down into product-wise sales and regional performance.</p>
        </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown("""
        <div class='feature-card'>
            <h4>Manage Expenses</h4>
            <p>Compare fixed and variable expenses and track cash flow.</p>
        </div>
    """, unsafe_allow_html=True)

# --- Capabilities Section ---
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
