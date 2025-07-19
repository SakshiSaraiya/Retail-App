import streamlit as st
import pandas as pd
import plotly.express as px
from db_connector import get_connection

# --- PAGE CONFIG ---
st.set_page_config(page_title="🛍️ Retail Dashboard", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
        background-color: #F9FAFB;
        color: #0F172A;
    }
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
        font-size: 0.9rem;
    }
    .stMetric {
        background-color: white;
        padding: 1.2rem;
        border-radius: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        height: 110px;
    }
    .stMetric > div > div:first-child {
        font-size: 1.1rem;
        font-weight: 600;
    }
    .stMetric > div > div:last-child {
        font-size: 1.5rem;
        font-weight: bold;
    }
    h1 {
        font-size: 3.2rem !important;
        font-weight: 700;
        text-align: center;
        margin-top: -10px;
        color: #0F172A;
    }
    h2 {
        font-size: 2rem !important;
        font-weight: 600;
        text-align: center;
        margin-top: -20px;
        color: #334155;
    }
    </style>
""", unsafe_allow_html=True)

# --- DB CONNECTION ---
conn = get_connection()
products_df = pd.read_sql("SELECT * FROM products", conn)
sales_df = pd.read_sql("SELECT * FROM sales", conn)
purchases_df = pd.read_sql("SELECT * FROM purchases", conn)

# --- SIDEBAR FILTERS ---
st.sidebar.title("🔍 Filter Dashboard")
selected_categories = st.sidebar.multiselect("Select Categories", products_df["category"].unique())
selected_products = st.sidebar.multiselect("Select Products", products_df["product_name"].unique())

# --- APPLY FILTERS ---
filtered_products_df = products_df.copy()
if selected_categories:
    filtered_products_df = filtered_products_df[filtered_products_df['category'].isin(selected_categories)]
if selected_products:
    filtered_products_df = filtered_products_df[filtered_products_df['product_name'].isin(selected_products)]

filtered_sales_df = sales_df[sales_df['product_name'].isin(filtered_products_df['product_name'])]

# --- METRICS CALCULATIONS ---
total_products = filtered_products_df['product_name'].nunique()
total_stock = filtered_products_df['stock_quantity'].sum()
total_revenue = filtered_sales_df['total_amount'].sum()
total_profit = filtered_sales_df['profit'].sum()
units_sold = filtered_sales_df['quantity'].sum()
profit_margin = (total_profit / total_revenue) * 100 if total_revenue != 0 else 0

# --- PAGE HEADER ---
st.markdown("<h1>Retail Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h2>Key Metrics</h2>", unsafe_allow_html=True)

# --- METRICS DISPLAY ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Products", total_products)
col2.metric("Total Stock", total_stock)
col3.metric("Units Sold", units_sold)

col4, col5, col6 = st.columns(3)
col4.metric("Total Revenue", f"₹ {total_revenue:,.2f}")
col5.metric("Total Profit", f"₹ {total_profit:,.2f}")
col6.metric("Profit Margin", f"{profit_margin:.1f}%")

# Highlights
st.markdown("###  Highlights")
top_product = sales_df.groupby('product_id')['quantity_sold'].sum().reset_index()
top_product = top_product.merge(filtered_products, on='product_id', how='left').sort_values(by='quantity_sold', ascending=False).head(1)

category_profit = sales_df.merge(filtered_products, on='product_id', how='left')
category_profit = category_profit.groupby('category')['profit'].sum().reset_index().sort_values(by='profit', ascending=False).head(1)

sales_df['sales_date'] = pd.to_datetime(sales_df['sales_date'], errors='coerce')
recent_sales = sales_df[sales_df['sales_date'] > pd.Timestamp.now() - pd.Timedelta(days=7)]
past_sales = sales_df[sales_df['sales_date'] <= pd.Timestamp.now() - pd.Timedelta(days=7)]
change = recent_sales['quantity_sold'].sum() - past_sales['quantity_sold'].sum()
trend_icon = "↑" if change >= 0 else "↓"

highlight_boxes = """
<div style="display: flex; gap: 1.2rem; justify-content: space-between;">
    <div class="highlight-box" style="flex: 1;">
        Best-Selling: <b>{}</b> ({} sold)
    </div>
    <div class="highlight-box" style="flex: 1;">
        Top Category: <b>{}</b> (₹ {:,.0f})
    </div>
    <div class="highlight-box" style="flex: 1;">
        Sales Trend: {} {} vs last 7 days
    </div>
</div>
"""

highlight_html = highlight_boxes.format(
    top_product.iloc[0]['product_name'] if not top_product.empty else "N/A",
    int(top_product.iloc[0]['quantity_sold']) if not top_product.empty else 0,
    category_profit.iloc[0]['category'] if not category_profit.empty else "N/A",
    category_profit.iloc[0]['profit'] if not category_profit.empty else 0,
    trend_icon,
    abs(change)
)

st.markdown(highlight_html, unsafe_allow_html=True)

# Low Stock
st.markdown("### ⚠️ Low Stock Alerts")
threshold = st.slider("Set stock threshold", 1, 50, 10)
live_inventory = filtered_products.merge(stock_merged[['product_id', 'live_stock']], on='product_id', how='left').fillna(0)
low_stock = live_inventory[live_inventory['live_stock'] < threshold]

if not low_stock.empty:
    st.error(f"⚠️ {len(low_stock)} product(s) are low on stock.")
    st.dataframe(low_stock[['product_id', 'product_name', 'live_stock']], use_container_width=True)
else:
    st.success("✅ All products have sufficient stock.")

# Monthly Sales Chart
st.markdown("###  Monthly Sales Overview")
sales_df = sales_df.dropna(subset=['sales_date'])
sales_df['month'] = sales_df['sales_date'].dt.to_period('M').astype(str)
monthly_metrics = sales_df.groupby('month').agg({
    'quantity_sold': 'sum',
    'selling_price': 'mean',
    'profit': 'sum'
}).reset_index()
monthly_metrics['revenue'] = monthly_metrics['quantity_sold'] * monthly_metrics['selling_price']

fig = px.line(monthly_metrics, x='month', y=['quantity_sold', 'revenue', 'profit'],
              color_discrete_sequence=['#1D4ED8', '#10B981', '#F59E0B'],
              markers=True, title="Monthly Sales Overview")
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis_title="Month",
    yaxis_title="Amount",
    legend_title_text="Metric"
)
st.plotly_chart(fig, use_container_width=True)

# Category-wise Sales Chart
st.markdown("###  Category-wise Sales")
category_sales = sales_df.merge(filtered_products, on='product_id', how='left')
category_grouped = category_sales.groupby('category')['quantity_sold'].sum().reset_index()

if not category_grouped.empty:
    category_fig = px.bar(category_grouped, x='category', y='quantity_sold',
                          title="Category-wise Sales", color='quantity_sold',
                          color_continuous_scale='Blues')
    category_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Category",
        yaxis_title="Units Sold"
    )
    st.plotly_chart(category_fig, use_container_width=True)
else:
    st.info("No sales data available to display category-wise insights.")
