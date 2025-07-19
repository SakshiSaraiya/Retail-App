import streamlit as st
import pandas as pd
import plotly.express as px
from db_connector import get_connection

# -------------------
# Page Configuration
# -------------------
st.set_page_config(page_title="Retail Dashboard", layout="wide")

# -------------
# Title
# -------------
st.markdown(
    "<h2 style='color:#0F172A;'>Retail Dashboard</h2>",
    unsafe_allow_html=True
)

# -------------------
# Connect to Database
# -------------------
db = get_connection()

# -------------------
# Load Data
# -------------------
product_df = pd.read_sql("SELECT * FROM product", db)
purchases_df = pd.read_sql("SELECT product_id, product_name, category, quantity_purchased, cost_price, order_date FROM purchases", db)
sales_df = pd.read_sql("SELECT product_id, quantity_sold, selling_price, sales_date FROM sales", db)

# Combine unique products from product and purchases
combined_products = pd.concat([
    product_df[['product_id', 'product_name', 'category']],
    purchases_df[['product_id', 'product_name', 'category']]
]).drop_duplicates(subset='product_id').reset_index(drop=True)

# -------------------
# Sidebar Filters
# -------------------
st.sidebar.markdown("## Filters")
category_filter = st.sidebar.multiselect(
    "Select Categories", combined_products['category'].dropna().unique(), default=combined_products['category'].unique()
)
product_filter = st.sidebar.multiselect(
    "Select Products", combined_products['product_name'].dropna().unique(), default=combined_products['product_name'].unique()
)

filtered_products = combined_products[
    (combined_products['category'].isin(category_filter)) &
    (combined_products['product_name'].isin(product_filter))
]
purchases_df = purchases_df[purchases_df['product_id'].isin(filtered_products['product_id'])]
sales_df = sales_df[sales_df['product_id'].isin(filtered_products['product_id'])]

# -------------------
# KPI Calculations
# -------------------
total_products = filtered_products['product_id'].nunique()

stock_df = purchases_df.groupby('product_id')['quantity_purchased'].sum().reset_index()
sold_df = sales_df.groupby('product_id')['quantity_sold'].sum().reset_index()
stock_merged = pd.merge(stock_df, sold_df, on='product_id', how='outer').fillna(0)
stock_merged['live_stock'] = stock_merged['quantity_purchased'] - stock_merged['quantity_sold']
total_stock_value = stock_merged['live_stock'].sum()

total_units_sold = sales_df['quantity_sold'].sum()
total_revenue = (sales_df['quantity_sold'] * sales_df['selling_price']).sum()

sales_profit = sales_df.merge(purchases_df[['product_id', 'cost_price']], on='product_id', how='left')
sales_profit['profit'] = sales_profit['quantity_sold'] * (sales_profit['selling_price'] - sales_profit['cost_price'])
total_profit = sales_profit['profit'].sum()

# -------------------
# KPI Display
# -------------------
st.markdown("#### Key Performance Indicators")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Products", total_products)
kpi2.metric("Total Stock", int(total_stock_value))
kpi3.metric("Units Sold", int(total_units_sold))
kpi4.metric("Total Revenue", f"₹ {total_revenue:,.2f}")
kpi5.metric("Total Profit", f"₹ {total_profit:,.2f}")

# -------------------
# Highlights
# -------------------
st.markdown("---")
st.markdown("#### Highlights")

top_product = sales_df.groupby('product_id')['quantity_sold'].sum().reset_index()
top_product = top_product.merge(filtered_products, on='product_id', how='left')
top_product = top_product.sort_values(by='quantity_sold', ascending=False).head(1)

category_profit = sales_profit.merge(filtered_products, on='product_id', how='left')
category_profit = category_profit.groupby('category')['profit'].sum().reset_index().sort_values(by='profit', ascending=False).head(1)

sales_df['sales_date'] = pd.to_datetime(sales_df['sales_date'], errors='coerce')
recent_sales = sales_df[sales_df['sales_date'] > pd.Timestamp.now() - pd.Timedelta(days=7)]
past_sales = sales_df[sales_df['sales_date'] <= pd.Timestamp.now() - pd.Timedelta(days=7)]
change = recent_sales['quantity_sold'].sum() - past_sales['quantity_sold'].sum()

h1, h2, h3 = st.columns(3)
with h1:
    if not top_product.empty:
        st.markdown(f"**Best-Selling Product:** {top_product.iloc[0]['product_name']} ({int(top_product.iloc[0]['quantity_sold'])} units)")
with h2:
    if not category_profit.empty:
        st.markdown(f"**Top Category:** {category_profit.iloc[0]['category']} (₹ {category_profit.iloc[0]['profit']:,.0f})")
with h3:
    direction = "Increase" if change >= 0 else "Decrease"
    st.markdown(f"**Sales Trend:** {direction} of {abs(change)} units vs. last 7 days")

# -------------------
# Low Stock Alerts
# -------------------
st.markdown("---")
st.markdown("#### Low Stock Alerts")
threshold = st.slider("Set stock threshold", 1, 50, 10)

live_inventory = filtered_products.merge(stock_merged[['product_id', 'live_stock']], on='product_id', how='left')
live_inventory['live_stock'].fillna(0, inplace=True)
low_stock = live_inventory[live_inventory['live_stock'] < threshold]

if not low_stock.empty:
    st.warning(f"{len(low_stock)} product(s) are low on stock.")
    st.dataframe(low_stock[['product_id', 'product_name', 'live_stock']], use_container_width=True)
else:
    st.success("All products have sufficient stock.")

# -------------------
# Monthly Sales Chart
# -------------------
st.markdown("---")
st.markdown("#### Monthly Sales Overview")

sales_df = sales_df.dropna(subset=['sales_date'])
sales_df['month'] = sales_df['sales_date'].dt.to_period('M').astype(str)

monthly_metrics = sales_df.groupby('month').agg({
    'quantity_sold': 'sum',
    'selling_price': 'mean'
}).reset_index()
monthly_metrics['revenue'] = monthly_metrics['quantity_sold'] * monthly_metrics['selling_price']

sales_df = sales_df.merge(purchases_df[['product_id', 'cost_price']], on='product_id', how='left')
sales_df['profit'] = sales_df['quantity_sold'] * (sales_df['selling_price'] - sales_df['cost_price'])
monthly_profit = sales_df.groupby('month')['profit'].sum().reset_index()

monthly_metrics = monthly_metrics.merge(monthly_profit, on='month', how='left')

fig = px.line(monthly_metrics, x='month', y=['quantity_sold', 'revenue', 'profit'],
              labels={'value': 'Amount', 'month': 'Month'}, markers=True, template='plotly_white')
fig.update_layout(
    legend_title_text='Metric',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig, use_container_width=True)

# -------------------
# Category-wise Sales
# -------------------
st.markdown("---")
st.markdown("#### Category-wise Sales Distribution")

category_sales = sales_df.merge(filtered_products, on='product_id', how='left')
category_grouped = category_sales.groupby('category')['quantity_sold'].sum().reset_index()

if not category_grouped.empty:
    fig2 = px.bar(category_grouped, x='category', y='quantity_sold', color='quantity_sold',
                  template='plotly_white', title="Units Sold by Category")
    fig2.update_layout(xaxis_title="Category", yaxis_title="Units Sold")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No sales data available to display category-wise insights.")
