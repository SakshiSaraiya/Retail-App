import streamlit as st

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Retail Compass",
    layout="wide"
)

# Optional: Custom CSS to improve sidebar and fonts
st.markdown("""
    <style>
        /* Sidebar styling */
        .css-6qob1r.eczjsme4 {
            background-color: #2c2f33;
        }
        .css-1d391kg {
            color: white;
        }

        /* Main title */
        h1 {
            font-family: 'Segoe UI', sans-serif;
            font-size: 42px;
            font-weight: bold;
        }

        /* Bullet list spacing */
        ul {
            padding-left: 20px;
            line-height: 1.6;
        }

        /* Button styling */
        .stButton > button {
            background-color: #4B6CB7;
            color: white;
            font-size: 16px;
            padding: 0.6em 2em;
            border-radius: 10px;
            border: none;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }

        .stButton > button:hover {
            background-color: #3c5799;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Main Title & Subtitle
# -------------------------------
st.markdown("<h1 style='text-align:center;'>Retail Compass</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px;'>A unified platform to manage inventory, sales, and finances efficiently.</p>", unsafe_allow_html=True)

# -------------------------------
# Feature Cards (3 columns)
# -------------------------------
st.markdown("<br>", unsafe_allow_html=True)
card_container = st.columns(3)

with card_container[0]:
    st.markdown("""
        <div style="background-color:#ffffff; color:#000000; padding:20px; border-radius:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align:center;">
            <h4>Inventory Overview</h4>
            <p style='font-size:14px;'>Monitor stock levels & categorize efficiently.</p>
        </div>
    """, unsafe_allow_html=True)

with card_container[1]:
    st.markdown("""
        <div style="background-color:#ffffff; color:#000000; padding:20px; border-radius:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align:center;">
            <h4>Sales Highlights</h4>
            <p style='font-size:14px;'>Track trends, products & profits with clarity.</p>
        </div>
    """, unsafe_allow_html=True)

with card_container[2]:
    st.markdown("""
        <div style="background-color:#ffffff; color:#000000; padding:20px; border-radius:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align:center;">
            <h4>Smart Suggestions</h4>
            <p style='font-size:14px;'>Automate reorder points & avoid stockouts.</p>
        </div>
    """, unsafe_allow_html=True)

# -------------------------------
# Capabilities Section
# -------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <h3>Platform Capabilities</h3>
    <ul style="font-size:16px;">
        <li>Inventory Management</li>
        <li>Sales Analysis and Forecasting</li>
        <li>Purchase & Vendor Tracking</li>
        <li>Financial Dashboards</li>
        <li>Expense Categorization and Reporting</li>
    </ul>
""", unsafe_allow_html=True)

# -------------------------------
# Navigation Buttons
# -------------------------------
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if st.button("📤 Upload Data"):
        st.switch_page("pages/0_upload_data.py")  # adjust path if needed

with btn_col2:
    if st.button("📊 View Inventory"):
        st.switch_page("pages/2_Inventory.py")  # adjust path if needed

# -------------------------------
# Optional Image (commented)
# -------------------------------
# st.image("images/retail_dashboard.png", use_column_width=True)

