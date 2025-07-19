import streamlit as st
import pandas as pd
import plotly.express as px
from db_connector import get_connection

st.set_page_config(page_title="Purchases", layout="wide")

# -------------------------
# Custom Styling
# -------------------------
st.markdown("""
    <style>
    body {
        background-color: #F9FAFB;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #1E293B;
    }

    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
        font-size: 0.95rem;
    }

    .metric-card {
        background-color: #1E293B;
        color: #FFFFFF;
        padding: 0.6rem 0.8rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 1rem;
        min-height: 80px;
    }
    .metric-card h4 {
        font-size: 1rem;
        margin-bottom: 0.25rem;
        color: #F8FAFC;
    }
    .metric-card h2 {
        font-size: 1.6rem;
        margin: 0;
        font-weight: 700;
        color: #FACC15;
    }
    h1, h2, h3, h4, h5, h6, p {
        color: #0F172A;
    }
    .dataframe tbody td {
        font-size: 0.95rem;
        color: #1F2937;
    }
    .dataframe thead th {
        background-color: #CBD5E1;
        font-weight: bold;
        color: #1E293B;
        font-size: 0.95rem;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# Title
# -------------------------
st.markdown("""
    <h2 style='margin-bottom: 1rem;'>Purchase Overview</h2>
""", unsafe_allow_html=True)

# -------------------------
# Connect to SQL
# -------------------------
conn = get_connection()

# -------------------------
# Load Data from SQL
# -------------------------
purchases = pd.read_sql("SELECT * FROM purchases", conn)
purchases['order_date'] = pd.to_datetime(purchases['order_date'], errors='coerce')
purchases['payment_due_date'] = pd.to_datetime(purchases['payment_due_date'], errors='coerce')

# -------------------------
# Compute KPIs
# -------------------------
total_orders = len(purchases)
total_quantity = purchases['quantity_purchased'].sum()
total_cost = (purchases['quantity_purchased'] * purchases['cost_price']).sum()
vendors = purchases['vendor_name'].nunique()

# -------------------------
# KPI Display
# -------------------------
st.markdown("<h4 style='margin-top:2rem;'>Key Metrics</h4>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Total Orders</h4>
            <h2>{total_orders}</h2>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Units Purchased</h4>
            <h2>{int(total_quantity)}</h2>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Total Spend</h4>
            <h2>₹ {total_cost:,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Vendors</h4>
            <h2>{vendors}</h2>
        </div>
    """, unsafe_allow_html=True)

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("Filter Purchases")
product_filter = st.sidebar.multiselect("Product", purchases['product_name'].dropna().unique(), default=purchases['product_name'].unique())
vendor_filter = st.sidebar.multiselect("Vendor", purchases['vendor_name'].dropna().unique(), default=purchases['vendor_name'].unique())
status_filter = st.sidebar.multiselect("Payment Status", purchases['payment_status'].dropna().unique(), default=purchases['payment_status'].unique())
start_date = st.sidebar.date_input("Start Date", purchases['order_date'].min())
end_date = st.sidebar.date_input("End Date", purchases['order_date'].max())

filtered = purchases[
    (purchases['product_name'].isin(product_filter)) &
    (purchases['vendor_name'].isin(vendor_filter)) &
    (purchases['payment_status'].isin(status_filter)) &
    (purchases['order_date'] >= pd.to_datetime(start_date)) &
    (purchases['order_date'] <= pd.to_datetime(end_date))
]

# -------------------------
# Display Filtered Table
# -------------------------
st.markdown("<h4 style='margin-top:2rem;'>Purchase Records</h4>", unsafe_allow_html=True)
expected_cols = ['product_id', 'product_name', 'category', 'vendor_name', 'quantity_purchased', 'cost_price', 'order_date', 'payment_due_date', 'payment_status']
available_cols = [col for col in expected_cols if col in filtered.columns]
st.dataframe(filtered[available_cols], use_container_width=True)

# ---------- Payment Alerts ----------
st.markdown("<h3 style='margin-top:2rem; color:#334155;'>Payment Alerts</h3>", unsafe_allow_html=True)
today = pd.to_datetime("today")
pending = filtered[filtered['payment_status'].str.lower() == "pending"]
overdue = filtered[(filtered['payment_status'].str.lower() != "paid") & (filtered['payment_due_date'] < today)]

col1, col2 = st.columns(2)

with col1:
    if not pending.empty:
        st.markdown("<div style='background-color:#FDE68A;padding:1rem;border-radius:0.5rem;'>", unsafe_allow_html=True)
        st.warning(f"Pending Payments: {len(pending)}")
        st.dataframe(pending[['vendor_name', 'product_name', 'payment_due_date']], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("No pending payments.")

with col2:
    if not overdue.empty:
        st.markdown("<div style='background-color:#FCA5A5;padding:1rem;border-radius:0.5rem;'>", unsafe_allow_html=True)
        st.error(f"Overdue Payments: {len(overdue)}")
        st.dataframe(overdue[['vendor_name', 'product_name', 'payment_due_date']], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("No overdue payments.")

# -------------------------
# Visualizations (Updated Layout & Color)
# -------------------------
st.markdown("---")

# Donut Chart for Vendors
col1, col2 = st.columns(2)

with col1:
    vendor_summary = filtered.groupby('vendor_name')['quantity_purchased'].sum().reset_index()
    fig_donut = px.pie(
        vendor_summary,
        names='vendor_name',
        values='quantity_purchased',
        title="Vendor Share",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_donut.update_layout(
        font=dict(family="Segoe UI", size=14, color="#0F172A"),
        showlegend=True,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF"
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# Top Products Chart
with col2:
    product_summary = filtered.groupby('product_name')['quantity_purchased'].sum().reset_index().sort_values(by='quantity_purchased', ascending=False)
    fig_product = px.bar(
        product_summary,
        x='product_name',
        y='quantity_purchased',
        title="Top Products by Purchase Volume",
        color='quantity_purchased',
        color_continuous_scale='Plasma'
    )
    fig_product.update_layout(
        xaxis_title="Product", yaxis_title="Quantity",
        font=dict(family="Segoe UI", size=14, color="#0F172A"),
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF"
    )
    st.plotly_chart(fig_product, use_container_width=True)

# Monthly Trend
monthly_summary = filtered.groupby(filtered['order_date'].dt.to_period('M').astype(str))['quantity_purchased'].sum().reset_index()
fig_monthly = px.area(
    monthly_summary,
    x='order_date',
    y='quantity_purchased',
    title="Monthly Purchase Volume",
    color_discrete_sequence=['#1D4ED8']
)
fig_monthly.update_layout(
    xaxis_title="Month", yaxis_title="Quantity",
    font=dict(family="Segoe UI", size=14, color="#0F172A"),
    plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF"
)
st.plotly_chart(fig_monthly, use_container_width=True)
