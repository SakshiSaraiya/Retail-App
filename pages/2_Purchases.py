# ✅ Updated: Professionally Styled Purchases Page

import streamlit as st
import pandas as pd
import plotly.express as px
from db_connector import get_connection

# -------------------------
# Page Config & Styling
# -------------------------
st.set_page_config(page_title="Purchases Dashboard", layout="wide")

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background-color: #F9FAFB;
    }

    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        text-align: center;
        height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .metric-card h4 {
        color: #475569;
        font-size: 0.9rem;
        margin: 0;
    }

    .metric-card h2 {
        color: #0F172A;
        font-size: 1.5rem;
        font-weight: 800;
        margin: 0;
    }

    .dataframe thead tr th {
        background-color: #E2E8F0;
        font-weight: bold;
        color: #1E293B;
    }

    .dataframe tbody tr td {
        color: #1F2937;
        font-size: 0.95rem;
    }

    .stAlert {
        background-color: #FEF3C7 !important;
        color: #92400E !important;
        border: 1px solid #FACC15 !important;
        font-weight: 500;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h2 style='color: #0F172A; font-weight: 800;'>Purchase Overview</h2>
<h4 style='color: #64748B;'>A summary of all your inbound inventory and vendor relationships</h4>
""", unsafe_allow_html=True)

# -------------------------
# Connect & Load
# -------------------------
conn = get_connection()
purchases = pd.read_sql("SELECT * FROM purchases", conn)
purchases['order_date'] = pd.to_datetime(purchases['order_date'], errors='coerce')
purchases['payment_due_date'] = pd.to_datetime(purchases['payment_due_date'], errors='coerce')

# -------------------------
# KPIs
# -------------------------
total_orders = len(purchases)
total_quantity = purchases['quantity_purchased'].sum()
total_cost = (purchases['quantity_purchased'] * purchases['cost_price']).sum()
vendors = purchases['vendor_name'].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='metric-card'><h4>Total Orders</h4><h2>{total_orders}</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-card'><h4>Units Purchased</h4><h2>{int(total_quantity)}</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-card'><h4>Total Spend</h4><h2>₹ {total_cost:,.2f}</h2></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='metric-card'><h4>Vendors</h4><h2>{vendors}</h2></div>", unsafe_allow_html=True)

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("Filter Purchases")
product_filter = st.sidebar.multiselect("Product", purchases['product_name'].dropna().unique(), default=purchases['product_name'].unique())
vendor_filter = st.sidebar.multiselect("Vendor", purchases['vendor_name'].dropna().unique(), default=purchases['vendor_name'].unique())
status_filter = st.sidebar.multiselect("Payment Status", purchases['payment_status'].dropna().unique(), default=purchases['payment_status'].unique())
start_date = st.sidebar.date_input("Start Date", purchases['order_date'].min())
end_date = st.sidebar.date_input("End Date", purchases['order_date'].max())

# -------------------------
# Apply filters
# -------------------------
filtered = purchases[
    (purchases['product_name'].isin(product_filter)) &
    (purchases['vendor_name'].isin(vendor_filter)) &
    (purchases['payment_status'].isin(status_filter)) &
    (purchases['order_date'] >= pd.to_datetime(start_date)) &
    (purchases['order_date'] <= pd.to_datetime(end_date))
]

# -------------------------
# Data Table
# -------------------------
st.markdown("### Purchase Records")
expected_cols = [
    'product_id', 'product_name', 'category', 'vendor_name',
    'quantity_purchased', 'cost_price', 'order_date', 'payment_due_date', 'payment_status']
filtered_cols = [col for col in expected_cols if col in filtered.columns]
st.dataframe(filtered[filtered_cols], use_container_width=True)

# -------------------------
# Payment Alerts
# -------------------------
st.markdown("---")
st.markdown("### Payment Alerts")
today = pd.to_datetime("today")
pending = filtered[filtered['payment_status'].str.lower() == "pending"]
overdue = filtered[(filtered['payment_status'].str.lower() != "paid") & (filtered['payment_due_date'] < today)]

c1, c2 = st.columns(2)
with c1:
    st.warning(f"Pending Payments: {len(pending)}")
    if not pending.empty:
        st.dataframe(pending[['vendor_name', 'product_name', 'payment_due_date']], use_container_width=True)

with c2:
    st.error(f"Overdue Payments: {len(overdue)}")
    if not overdue.empty:
        st.dataframe(overdue[['vendor_name', 'product_name', 'payment_due_date']], use_container_width=True)

# -------------------------
# Visualizations (Improved)
# -------------------------
st.markdown("---")

vendor_summary = filtered.groupby('vendor_name')['quantity_purchased'].sum().reset_index()
fig_vendor = px.bar(
    vendor_summary,
    x='vendor_name',
    y='quantity_purchased',
    title="Quantity Purchased by Vendor",
    color='vendor_name',
    text='quantity_purchased',
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig_vendor.update_traces(textposition="outside")
fig_vendor.update_layout(
    xaxis_title="Vendor", yaxis_title="Quantity", legend_title="Vendor",
    font=dict(family="Segoe UI", size=14, color="#0F172A"),
    plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF"
)
st.plotly_chart(fig_vendor, use_container_width=True)

monthly_summary = filtered.groupby(filtered['order_date'].dt.to_period('M').astype(str))['quantity_purchased'].sum().reset_index()
fig_monthly = px.line(
    monthly_summary,
    x='order_date',
    y='quantity_purchased',
    title="Monthly Purchase Volume",
    markers=True,
    color_discrete_sequence=['#1D4ED8']
)
fig_monthly.update_layout(
    xaxis_title="Month", yaxis_title="Quantity",
    font=dict(family="Segoe UI", size=14, color="#0F172A"),
    plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF"
)
st.plotly_chart(fig_monthly, use_container_width=True)

product_summary = filtered.groupby('product_name')['quantity_purchased'].sum().reset_index().sort_values(by='quantity_purchased', ascending=False)
fig_product = px.bar(
    product_summary,
    x='product_name',
    y='quantity_purchased',
    title="Top Products by Purchase Volume",
    color='quantity_purchased',
    color_continuous_scale='Blues'
)
fig_product.update_layout(
    xaxis_title="Product", yaxis_title="Quantity",
    font=dict(family="Segoe UI", size=14, color="#0F172A"),
    plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF"
)
st.plotly_chart(fig_product, use_container_width=True)
