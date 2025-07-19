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
        padding: 0.75rem 1rem;
        border-radius: 0.75rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        text-align: left;
        margin-bottom: 1rem;
        min-height: 110px;
    }
    .metric-card h4 {
        font-size: 1rem;
        margin: 0 0 0.4rem 0;
        color: #94A3B8;
    }
    .metric-card h2 {
        font-size: 1.8rem;
        margin: 0;
        font-weight: 800;
        color: #FACC15;
    }
    .metric-card span {
        display: block;
        font-size: 0.8rem;
        margin-top: 0.3rem;
        color: #A5B4FC;
    }

    h1, h2, h3, h4, h5, h6, p {
        color: #0F172A;
    }

    .dataframe tbody td {
        font-size: 0.95rem;
        color: #1F2937;
    }
    .dataframe thead th {
        background-color: #1E293B;
        font-weight: bold;
        color: #F1F5F9;
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
            <span>Across all vendors</span>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Units Purchased</h4>
            <h2>{int(total_quantity)}</h2>
            <span>In current timeframe</span>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Total Spend</h4>
            <h2>₹ {total_cost:,.2f}</h2>
            <span>Gross purchase cost</span>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Unique Vendors</h4>
            <h2>{vendors}</h2>
            <span>Active suppliers</span>
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
        st.warning(f"Pending Payments: {len(pending)}")
        st.dataframe(pending[['vendor_name', 'product_name', 'payment_due_date']], use_container_width=True)
    else:
        st.success("No pending payments.")

with col2:
    if not overdue.empty:
        st.error(f"Overdue Payments: {len(overdue)}")
        st.dataframe(overdue[['vendor_name', 'product_name', 'payment_due_date']], use_container_width=True)
    else:
        st.success("No overdue payments.")

# -------------------------
# Visualizations (Improved)
# -------------------------
st.markdown("---")

# Donut Chart - Vendor-wise share
vendor_share = filtered.groupby('vendor_name')['quantity_purchased'].sum().reset_index()
fig_donut = px.pie(
    vendor_share,
    names='vendor_name',
    values='quantity_purchased',
    title="Vendor Share by Quantity",
    hole=0.5,
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_donut.update_layout(showlegend=True, plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
st.plotly_chart(fig_donut, use_container_width=True)

# Area Chart - Monthly trend
monthly_summary = filtered.groupby(filtered['order_date'].dt.to_period('M').astype(str))['quantity_purchased'].sum().reset_index()
fig_area = px.area(
    monthly_summary,
    x='order_date',
    y='quantity_purchased',
    title="Monthly Purchase Volume",
    color_discrete_sequence=['#0EA5E9']
)
fig_area.update_layout(
    xaxis_title="Month", yaxis_title="Quantity",
    font=dict(family="Segoe UI", size=14, color="#0F172A"),
    plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF"
)
st.plotly_chart(fig_area, use_container_width=True)

# Horizontal bar - Top products
product_summary = filtered.groupby('product_name')['quantity_purchased'].sum().reset_index().sort_values(by='quantity_purchased', ascending=True)
fig_barh = px.bar(
    product_summary,
    x='quantity_purchased',
    y='product_name',
    title="Top Products by Volume",
    orientation='h',
    color='quantity_purchased',
    color_continuous_scale='Agsunset'
)
fig_barh.update_layout(
    xaxis_title="Quantity", yaxis_title="Product",
    font=dict(family="Segoe UI", size=14, color="#0F172A"),
    plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF"
)
st.plotly_chart(fig_barh, use_container_width=True)
