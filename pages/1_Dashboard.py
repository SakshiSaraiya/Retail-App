# 📊 Retail Dashboard - Professionally Styled & Enhanced  
import streamlit as st
import pandas as pd
import plotly.express as px
from db_connector import get_connection

# Page Config
st.set_page_config(page_title="📊 Retail Dashboard", layout="wide")

# Styling Variables
SIDEBAR_COLOR = "#0F172A"
BG_COLOR = "#F9FAFB"
CARD_BG = "#FFFFFF"
HIGHLIGHT_BG = "#1E293B"
TEXT_COLOR = "#0F172A"
FONT_FAMILY = "'Segoe UI', 'Roboto', sans-serif"

# Inject CSS
st.markdown(
    f"""
    <style>
        html, body, [class*="css"] {{
            background-color: {BG_COLOR};
            font-family: {FONT_FAMILY};
        }}

        [data-testid="stSidebar"] {{
            background-color: {SIDEBAR_COLOR};
            color: white;
        }}

        [data-testid="stSidebar"] * {{
            color: #E2E8F0 !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
        }}

        .highlight-box {{
            background-color: {HIGHLIGHT_BG};
            color: white;
            padding: 0.9rem 1rem;
            border-radius: 1rem;
            font-weight: 500;
            font-size: 0.9rem;
            box-shadow: 0 3px 6px rgba(0,0,0,0.08);
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }}

        .highlight-box b {{
            color: #FACC15;
        }}

        footer {{ visibility: hidden; }}
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown("""
    <h1 style='text-align: center; font-size: 2.8rem; font-weight: 900; margin-bottom: 0.2rem; color: #0F172A;'>Retail Dashboard</h1>
    <h3 style='text-align: center; font-size: 1.4rem; font-weight: 600; margin-bottom: 1.5rem; color: #334155;'>Key Metrics</h3>
""", unsafe_allow_html=True)

# DB Connection
db = get_connection()

# Load Data
product_df = pd.read_sql("SELECT * FROM product", db)
purchases_df = pd.read_sql("SELECT product_id, product_name, category, quantity_purchased, cost_price, order_date FROM purchases", db)
sales_df = pd.read_sql("SELECT product_id, quantity_sold, selling_price, sales_date FROM sales", db)

# Merge product info
combined_products = pd.concat([
    product_df[['product_id', 'product_name', 'category']],
    purchases_df[['product_id', 'product_name', 'category']]
]).drop_duplicates('product_id')

# Sidebar Filters
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

# Profit
sales_df = sales_df.merge(purchases_df[['product_id', 'cost_price']], on='product_id', how='left')
sales_df['profit'] = sales_df['quantity_sold'] * (sales_df['selling_price'] - sales_df['cost_price'])

# KPIs
total_products = filtered_products['product_id'].nunique()
total_stock_value = stock_merged['live_stock'].sum()
total_units_sold = sales_df['quantity_sold'].sum()
total_revenue = (sales_df['quantity_sold'] * sales_df['selling_price']).sum()
total_profit = sales_df['profit'].sum()
profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0

# Metric Cards
def render_metric(title, value):
    return f"""
    <div style='
        background-color: #FFFFFF;
        padding: 1rem;
        height: 110px;
        border-radius: 1rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    '>
        <h4 style='font-size: 0.85rem; color: #64748B; margin: 0;'>{title}</h4>
        <h2 style='font-size: 1.4rem; color: #0F172A; margin: 0; font-weight: 700;'>{value}</h2>
    </div>
    """

col1, col2, col3 = st.columns(3)
col1.markdown(render_metric("Total Products", total_products), unsafe_allow_html=True)
col2.markdown(render_metric("Total Stock", int(total_stock_value)), unsafe_allow_html=True)
col3.markdown(render_metric("Units Sold", int(total_units_sold)), unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)
col4.markdown(render_metric("Total Revenue", f"₹ {total_revenue:,.2f}"), unsafe_allow_html=True)
col5.markdown(render_metric("Total Profit", f"₹ {total_profit:,.2f}"), unsafe_allow_html=True)
col6.markdown(render_metric("Profit Margin", f"{profit_margin:.1f}%"), unsafe_allow_html=True)

# Highlights
st.markdown("### Highlights")
top_product = sales_df.groupby('product_id')['quantity_sold'].sum().reset_index()
top_product = top_product.merge(filtered_products, on='product_id', how='left').sort_values(by='quantity_sold', ascending=False).head(1)

category_profit = sales_df.merge(filtered_products, on='product_id', how='left')
category_profit = category_profit.groupby('category')['profit'].sum().reset_index().sort_values(by='profit', ascending=False).head(1)

sales_df['sales_date'] = pd.to_datetime(sales_df['sales_date'], errors='coerce')
recent_sales = sales_df[sales_df['sales_date'] > pd.Timestamp.now() - pd.Timedelta(days=7)]
past_sales = sales_df[sales_df['sales_date'] <= pd.Timestamp.now() - pd.Timedelta(days=7)]
change = recent_sales['quantity_sold'].sum() - past_sales['quantity_sold'].sum()
trend_icon = "↑" if change >= 0 else "↓"

highlight_boxes = f"""
<div style="display: flex; gap: 1rem;">
    <div class="highlight-box">Best-Selling: <b>{top_product.iloc[0]['product_name'] if not top_product.empty else "N/A"}</b> ({int(top_product.iloc[0]['quantity_sold']) if not top_product.empty else 0} sold)</div>
    <div class="highlight-box">Top Category: <b>{category_profit.iloc[0]['category'] if not category_profit.empty else "N/A"}</b> (₹ {category_profit.iloc[0]['profit']:,.0f})</div>
    <div class="highlight-box">Sales Trend: {trend_icon} {abs(change)} vs last 7 days</div>
</div>
"""
st.markdown(highlight_boxes, unsafe_allow_html=True)

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
