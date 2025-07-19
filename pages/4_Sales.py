import streamlit as st 
import pandas as pd
import plotly.express as px
from db_connector import get_connection

st.set_page_config(page_title="📈 Sales", layout="wide")

# -------------------------
# Custom CSS
# -------------------------
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    h1, h2, h3, h4, h5, h6, p {
        color: #0F172A;
    }
    .metric-card {
        background-color: #1E293B;
        color: #FFFFFF;
        padding: 0.8rem;
        border-radius: 0.75rem;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    .metric-card h4 {
        font-size: 1rem;
        color: #CBD5E1;
        margin-bottom: 0.3rem;
    }
    .metric-card h2 {
        font-size: 1.7rem;
        color: #FACC15;
        font-weight: bold;
        margin: 0;
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

# Revenue and Profit
sales['revenue'] = sales['quantity_sold'] * sales['selling_price']
sales['profit'] = sales['quantity_sold'] * (sales['selling_price'] - sales['cost_price'])

# -------------------------
# Filters
# -------------------------
st.sidebar.header("🔍 Filter Sales")
product_filter = st.sidebar.multiselect("Product Name", sales['product_name'].dropna().unique(), default=sales['product_name'].unique())
shipped_filter = st.sidebar.selectbox("Shipped Status", ["All"] + sales['shipped_status'].dropna().unique().tolist())
payment_filter = st.sidebar.selectbox("Payment Status", ["All"] + sales['payment_status'].dropna().unique().tolist())
start_date = st.sidebar.date_input("Start Date", value=sales['sales_date'].min())
end_date = st.sidebar.date_input("End Date", value=sales['sales_date'].max())

filtered_sales = sales[(sales['product_name'].isin(product_filter)) &
                       (sales['sales_date'] >= pd.to_datetime(start_date)) &
                       (sales['sales_date'] <= pd.to_datetime(end_date))]

if shipped_filter != "All":
    filtered_sales = filtered_sales[filtered_sales['shipped_status'] == shipped_filter]
if payment_filter != "All":
    filtered_sales = filtered_sales[filtered_sales['payment_status'] == payment_filter]

# -------------------------
# KPI Metrics
# -------------------------
st.markdown("### 📊 Sales KPIs")
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Total Sales</h4>
            <h2>{int(filtered_sales['quantity_sold'].sum())}</h2>
        </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Total Revenue</h4>
            <h2>₹ {filtered_sales['revenue'].sum():,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Total Profit</h4>
            <h2>₹ {filtered_sales['profit'].sum():,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Orders</h4>
            <h2>{len(filtered_sales)}</h2>
        </div>
    """, unsafe_allow_html=True)

# -------------------------
# Transactions Table
# -------------------------
st.markdown("### 📋 Sales Transactions")
if filtered_sales.empty:
    st.warning("⚠️ No matching sales records found with current filters.")
else:
    st.dataframe(filtered_sales[['sale_id', 'sales_date', 'product_name', 'quantity_sold', 'revenue', 'profit', 'shipped_status', 'payment_status']], use_container_width=True)

# -------------------------
# Top Products
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
    fig1 = px.bar(top_products, x='product_name', y='quantity_sold', title="Top Products by Quantity", color='quantity_sold', color_continuous_scale='Blues')
    fig1.update_layout(xaxis_title="Product", yaxis_title="Quantity")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(top_products, x='product_name', y='revenue', title="Top Products by Revenue", color='revenue', color_continuous_scale='Greens')
    fig2.update_layout(xaxis_title="Product", yaxis_title="Revenue")
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# Combined Monthly Trends
# -------------------------
st.markdown("---")
st.markdown("### 📆 Monthly Sales Performance")
monthly_grouped = filtered_sales.copy()
monthly_grouped['month'] = monthly_grouped['sales_date'].dt.to_period('M').astype(str)
monthly_grouped = monthly_grouped.groupby('month')[['quantity_sold', 'revenue', 'profit']].sum().reset_index()

fig_combined = px.line(monthly_grouped, x='month', y=['quantity_sold', 'revenue', 'profit'], markers=True,
                       title="Monthly Sales Metrics", labels={'value': 'Amount', 'variable': 'Metric'})
fig_combined.update_layout(xaxis_title="Month", yaxis_title="Value", legend_title="Metric")
st.plotly_chart(fig_combined, use_container_width=True)

# -------------------------
# Forecasting
# -------------------------
st.markdown("---")
st.markdown("### 🔮 Sales Forecast by Product")

sales_forecast = pd.merge(sales, purchases[['product_id', 'product_name']], on='product_id', how='left')
sales_forecast['sales_date'] = pd.to_datetime(sales_forecast['sales_date'], errors='coerce')

selected_product = st.selectbox("Select Product for Forecast", sorted(sales_forecast['product_name'].dropna().unique()))
product_sales = sales_forecast[sales_forecast['product_name'] == selected_product].copy()

product_sales['month'] = product_sales['sales_date'].dt.to_period('M').astype(str)
monthly_sales = product_sales.groupby('month')['quantity_sold'].sum().reset_index()
monthly_sales['month'] = pd.to_datetime(monthly_sales['month'])
monthly_sales = monthly_sales.sort_values('month')
monthly_sales['forecast_qty'] = monthly_sales['quantity_sold'].rolling(window=3, min_periods=1).mean()

last_month = monthly_sales['month'].max()
forecast_months = pd.date_range(start=last_month + pd.offsets.MonthBegin(), periods=3, freq='MS')
last_forecast = monthly_sales['forecast_qty'].iloc[-1]

future_forecast = pd.DataFrame({
    'month': forecast_months,
    'quantity_sold': [None]*3,
    'forecast_qty': [last_forecast]*3
})

forecast_df = pd.concat([monthly_sales, future_forecast], ignore_index=True)

fig = px.line(forecast_df, x='month', y='forecast_qty', title=f"📈 Forecasted Sales for '{selected_product}'",
              labels={'forecast_qty': 'Forecasted Quantity'}, markers=True)
fig.add_scatter(x=monthly_sales['month'], y=monthly_sales['quantity_sold'], mode='lines+markers', name='Actual Quantity', line=dict(color='orange'))
st.plotly_chart(fig, use_container_width=True)
