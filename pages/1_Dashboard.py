# 📊 Retail Dashboard - Professionally Styled & Enhanced
import streamlit as st
import pandas as pd
import plotly.express as px
from db_connector import get_connection

# Page Config
st.set_page_config(page_title="📊 Retail Dashboard", layout="wide")

# Styling Theme Variables
SIDEBAR_COLOR = "#0F172A"
BG_COLOR = "#F9FAFB"
CARD_BG = "#FFFFFF"
HIGHLIGHT_BG = "#1E293B"
TEXT_COLOR = "#0F172A"
FONT_FAMILY = "'Segoe UI', 'Roboto', sans-serif"

# Custom CSS Styling Block
st.markdown(
    f"""
    <style>
        html, body, [class*="css"] {{
            background-color: {BG_COLOR};
            font-family: {FONT_FAMILY};
        }}

        [data-testid="stSidebar"] > div:first-child {{
            background-color: {SIDEBAR_COLOR};
            color: white;
            padding: 1.5rem;
        }}

        .stMultiSelect, .stSelectbox, .stSlider {{
            color: white !important;
        }}

        .metric-card {{
            background-color: {CARD_BG};
            padding: 1.4rem 1rem;
            border-radius: 1rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s ease;
            height: 100px;
        }}
        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
        }}
        .metric-card h4 {{
            font-size: 0.95rem;
            color: #64748b;
            margin-bottom: 0.3rem;
            font-weight: 500;
        }}
        .metric-card h2 {{
            font-size: 1.7rem;
            color: {TEXT_COLOR};
            margin-top: 0;
            font-weight: 600;
        }}

        .highlight-box {{
            background-color: {HIGHLIGHT_BG};
            color: white;
            padding: 1.2rem;
            border-radius: 1rem;
            font-weight: 500;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }}

        footer {{
            visibility: hidden;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Retail Dashboard")

# Connect to DB
db = get_connection()

# Load data
product_df = pd.read_sql("SELECT * FROM product", db)
purchases_df = pd.read_sql("SELECT product_id, product_name, category, quantity_purchased, cost_price, order_date FROM purchases", db)
sales_df = pd.read_sql("SELECT product_id, quantity_sold, selling_price, sales_date FROM sales", db)

# Merge product info
combined_products = pd.concat([
    product_df[['product_id', 'product_name', 'category']],
    purchases_df[['product_id', 'product_name', 'category']]
]).drop_duplicates('product_id')

# Sidebar
st.sidebar.header("🔍 Filter Dashboard")
category_filter = st.sidebar.multiselect("Select Categories", combined_products['category'].dropna().unique(), default=combined_products['category'].unique())
product_filter = st.sidebar.multiselect("Select Products", combined_products['product_name'].dropna().unique(), default=combined_products['product_name'].unique())

# Apply filters
filtered_products = combined_products[
    combined_products['category'].isin(category_filter) & 
    combined_products['product_name'].isin(product_filter)
]
purchases_df = purchases_df[purchases_df['product_id'].isin(filtered_products['product_id'])]
sales_df = sales_df[sales_df['product_id'].isin(filtered_products['product_id'])]

# Inventory & Sales
stock_df = purchases_df.groupby('product_id')['quantity_purchased'].sum().reset_index()
sold_df = sales_df.groupby('product_id')['quantity_sold'].sum().reset_index()
stock_merged = pd.merge(stock_df, sold_df, on='product_id', how='outer').fillna(0)
stock_merged['live_stock'] = stock_merged['quantity_purchased'] - stock_merged['quantity_sold']

# Profit calculation
sales_df = sales_df.merge(purchases_df[['product_id', 'cost_price']], on='product_id', how='left')
sales_df['profit'] = sales_df['quantity_sold'] * (sales_df['selling_price'] - sales_df['cost_price'])

# KPIs
total_products = filtered_products['product_id'].nunique()
total_stock_value = stock_merged['live_stock'].sum()
total_units_sold = sales_df['quantity_sold'].sum()
total_revenue = (sales_df['quantity_sold'] * sales_df['selling_price']).sum()
total_profit = sales_df['profit'].sum()

# Metrics Display
st.markdown("### 📌 Key Metrics")
m1, m2, m3 = st.columns(3)
with m1:
    m1.markdown(f"<div class='metric-card'><h4>Total Products</h4><h2>{total_products}</h2></div>", unsafe_allow_html=True)
with m2:
    m2.markdown(f"<div class='metric-card'><h4>Total Stock</h4><h2>{int(total_stock_value)}</h2></div>", unsafe_allow_html=True)
with m3:
    m3.markdown(f"<div class='metric-card'><h4>Units Sold</h4><h2>{int(total_units_sold)}</h2></div>", unsafe_allow_html=True)

m4, m5 = st.columns(2)
with m4:
    m4.markdown(f"<div class='metric-card'><h4>Total Revenue</h4><h2>₹ {total_revenue:,.2f}</h2></div>", unsafe_allow_html=True)
with m5:
    m5.markdown(f"<div class='metric-card'><h4>Total Profit</h4><h2>₹ {total_profit:,.2f}</h2></div>", unsafe_allow_html=True)

# Highlights
st.markdown("### 🏆 Highlights")
top_product = sales_df.groupby('product_id')['quantity_sold'].sum().reset_index()
top_product = top_product.merge(filtered_products, on='product_id', how='left').sort_values(by='quantity_sold', ascending=False).head(1)

category_profit = sales_df.merge(filtered_products, on='product_id', how='left')
category_profit = category_profit.groupby('category')['profit'].sum().reset_index().sort_values(by='profit', ascending=False).head(1)

sales_df['sales_date'] = pd.to_datetime(sales_df['sales_date'], errors='coerce')
recent_sales = sales_df[sales_df['sales_date'] > pd.Timestamp.now() - pd.Timedelta(days=7)]
past_sales = sales_df[sales_df['sales_date'] <= pd.Timestamp.now() - pd.Timedelta(days=7)]
change = recent_sales['quantity_sold'].sum() - past_sales['quantity_sold'].sum()
trend_icon = "↑" if change >= 0 else "↓"

h1, h2, h3 = st.columns(3)
if not top_product.empty:
    h1.markdown(f"<div class='highlight-box'>🔥 Best-Selling: <b>{top_product.iloc[0]['product_name']}</b> ({int(top_product.iloc[0]['quantity_sold'])} sold)</div>", unsafe_allow_html=True)
if not category_profit.empty:
    h2.markdown(f"<div class='highlight-box'>📊 Top Category: <b>{category_profit.iloc[0]['category']}</b> (₹ {category_profit.iloc[0]['profit']:,.0f})</div>", unsafe_allow_html=True)
h3.markdown(f"<div class='highlight-box'>📈 Sales Trend: {trend_icon} {abs(change)} vs last 7 days</div>", unsafe_allow_html=True)

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

# Monthly Chart
st.markdown("### 📅 Monthly Sales Overview")
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

# Category-wise Sales
st.markdown("### 📦 Category-wise Sales")
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
