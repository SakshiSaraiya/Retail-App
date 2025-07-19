import streamlit as st 
import pandas as pd
import plotly.express as px
from db_connector import get_connection

st.set_page_config(page_title="📈 Sales", layout="wide")

# -------------------------
# Custom Styling
# -------------------------
st.markdown("""
    <style>
    body {
        background-color: #F8FAFC;
        font-family: 'Segoe UI', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
        font-size: 0.95rem;
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

st.title("📈 Sales Overview")

# -------------------------
# Connect to MySQL
# -------------------------
conn = get_connection()

# -------------------------
# Load raw tables
# -------------------------
try:
    sales = pd.read_sql("SELECT * FROM sales", conn)
    products = pd.read_sql("SELECT * FROM product", conn)
    purchases = pd.read_sql("SELECT product_id, product_name AS product_name_purchases, cost_price FROM purchases", conn)
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# Normalize product_id
sales['product_id'] = sales['product_id'].astype(str).str.strip().str.upper()
products['product_id'] = products['product_id'].astype(str).str.strip().str.upper()
purchases['product_id'] = purchases['product_id'].astype(str).str.strip().str.upper()

# Merge product info
sales = sales.merge(products, on='product_id', how='left')
sales = sales.merge(purchases, on='product_id', how='left')
sales['product_name'] = sales['product_name'].fillna(sales['product_name_purchases'])

# Parse sales_date
sales['sales_date'] = pd.to_datetime(sales['sales_date'], errors='coerce')

# Calculate revenue & profit
sales['revenue'] = sales['quantity_sold'] * sales['selling_price']
sales['profit'] = sales['quantity_sold'] * (sales['selling_price'] - sales['cost_price'])

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("🔍 Filter Sales")
product_filter = st.sidebar.multiselect("Product Name", sales['product_name'].dropna().unique(), default=sales['product_name'].dropna().unique())
shipped_filter = st.sidebar.selectbox("Shipped Status", ["All"] + sales['shipped_status'].dropna().unique().tolist())
payment_filter = st.sidebar.selectbox("Payment Status", ["All"] + sales['payment_status'].dropna().unique().tolist())
start_date = st.sidebar.date_input("Start Date", value=sales['sales_date'].min())
end_date = st.sidebar.date_input("End Date", value=sales['sales_date'].max())

# -------------------------
# Apply Filters
# -------------------------
filtered_sales = sales[
    (sales['product_name'].isin(product_filter)) &
    (sales['sales_date'] >= pd.to_datetime(start_date)) &
    (sales['sales_date'] <= pd.to_datetime(end_date))
]
if shipped_filter != "All":
    filtered_sales = filtered_sales[filtered_sales['shipped_status'] == shipped_filter]
if payment_filter != "All":
    filtered_sales = filtered_sales[filtered_sales['payment_status'] == payment_filter]

# -------------------------
# KPI Metrics
# -------------------------
st.markdown("### 📊 Sales KPIs")
k1, k2, k3, k4 = st.columns(4)
k1.metric("🧾 Total Sales", int(filtered_sales['quantity_sold'].sum()))
k2.metric("💰 Total Revenue", f"₹ {filtered_sales['revenue'].sum():,.2f}")
k3.metric("📈 Total Profit", f"₹ {filtered_sales['profit'].sum():,.2f}")
k4.metric("🛍️ Orders", len(filtered_sales))

# -------------------------
# Display Sales Data
# -------------------------
st.markdown("### 📋 Sales Transactions")
if filtered_sales.empty:
    st.warning("⚠️ No matching sales records found with current filters.")
else:
    st.dataframe(filtered_sales[['sale_id', 'sales_date', 'product_name', 'quantity_sold', 'revenue', 'profit', 'shipped_status', 'payment_status']], use_container_width=True)

# -------------------------
# Top Products Section
# -------------------------
st.markdown("---")
st.markdown("### 🏆 Top-Selling Products")
top_n = st.slider("Top N Products", 5, 20, 10)
top_products = filtered_sales.groupby('product_name').agg({
    'quantity_sold': 'sum',
    'revenue': 'sum',
    'profit': 'sum'
}).sort_values(by='quantity_sold', ascending=False).reset_index().head(top_n)

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(top_products, x='product_name', y='quantity_sold', title=f"Top {top_n} Products by Quantity", color='quantity_sold', color_continuous_scale='Blues')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(top_products, x='product_name', y='revenue', title=f"Top {top_n} Products by Revenue", color='revenue', color_continuous_scale='Viridis')
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# Monthly Trend Charts
# -------------------------
st.markdown("---")
st.markdown("### 📆 Monthly Sales Performance")
monthly_grouped = filtered_sales.copy()
monthly_grouped['month'] = monthly_grouped['sales_date'].dt.to_period('M').astype(str)
monthly_agg = monthly_grouped.groupby('month')[['quantity_sold', 'revenue', 'profit']].sum().reset_index()

st.plotly_chart(px.line(monthly_agg, x='month', y='quantity_sold', title="Monthly Units Sold", markers=True, color_discrete_sequence=['#0F172A']), use_container_width=True)
st.plotly_chart(px.line(monthly_agg, x='month', y='revenue', title="Monthly Revenue", markers=True, color_discrete_sequence=['#059669']), use_container_width=True)
st.plotly_chart(px.line(monthly_agg, x='month', y='profit', title="Monthly Profit", markers=True, color_discrete_sequence=['#EF4444']), use_container_width=True)

# -------------------------
# 🔮 Forecasting
# -------------------------
st.markdown("---")
st.markdown("### 🔮 Sales Forecast")
sales_forecast = sales.copy()
sales_forecast['sales_date'] = pd.to_datetime(sales_forecast['sales_date'], errors='coerce')
sales_forecast['month'] = sales_forecast['sales_date'].dt.to_period('M').astype(str)

selected_product = st.selectbox("Select Product", sorted(sales_forecast['product_name'].dropna().unique()))
product_sales = sales_forecast[sales_forecast['product_name'] == selected_product].copy()
monthly_sales = product_sales.groupby('month')['quantity_sold'].sum().reset_index()
monthly_sales['month'] = pd.to_datetime(monthly_sales['month'])
monthly_sales = monthly_sales.sort_values('month')
monthly_sales['forecast_qty'] = monthly_sales['quantity_sold'].rolling(3, min_periods=1).mean()

future_months = pd.date_range(start=monthly_sales['month'].max() + pd.offsets.MonthBegin(), periods=3, freq='MS')
last_forecast = monthly_sales['forecast_qty'].iloc[-1]
future_df = pd.DataFrame({
    'month': future_months,
    'forecast_qty': [last_forecast]*3
})
forecast_df = pd.concat([monthly_sales[['month', 'quantity_sold', 'forecast_qty']], future_df], ignore_index=True)

fig = px.line(forecast_df, x='month', y='forecast_qty', title=f"Forecast for {selected_product}", markers=True, color_discrete_sequence=['#6366F1'])
fig.add_scatter(x=monthly_sales['month'], y=monthly_sales['quantity_sold'], mode='lines+markers', name='Actual', line=dict(color='orange'))
st.plotly_chart(fig, use_container_width=True)
