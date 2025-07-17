import streamlit as st
import pandas as pd
import plotly.express as px
from db_connector import get_connection

st.set_page_config(page_title="💹 Finance Dashboard", layout="wide")
st.title("💹 Financial Health Dashboard")

# -------------------------
# Connect to Database
# -------------------------
conn = get_connection()

# -------------------------
# Load Data
# -------------------------
purchases = pd.read_sql("SELECT * FROM purchases", conn)
sales = pd.read_sql("SELECT * FROM sales", conn)
products = pd.read_sql("SELECT * FROM inventory", conn)

# -------------------------
# Merge Purchase and Sales
# -------------------------
sales = sales.merge(purchases[['product_id', 'cost_price']], on='product_id', how='left')
sales = sales.merge(products[['product_id', 'category']], on='product_id', how='left')

# Compute Profit per Transaction
sales['revenue'] = sales['selling_price'] * sales['quantity_sold']
sales['cost'] = sales['cost_price'] * sales['quantity_sold']
sales['profit'] = sales['revenue'] - sales['cost']

# -------------------------
# KPIs
# -------------------------
total_revenue = sales['revenue'].sum()
total_cost = sales['cost'].sum()
total_profit = sales['profit'].sum()
profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"₹{total_revenue:,.2f}")
col2.metric("💸 Total Cost", f"₹{total_cost:,.2f}")
col3.metric("📈 Gross Profit", f"₹{total_profit:,.2f}")
col4.metric("📊 Profit Margin", f"{profit_margin:.2f}%")

# -------------------------
# Monthly Cash Flow
# -------------------------
sales['sales_date'] = pd.to_datetime(sales['sales_date'])
purchases['order_date'] = pd.to_datetime(purchases['order_date'])

monthly_sales = sales.groupby(sales['sales_date'].dt.to_period('M')).agg({
    'revenue': 'sum'
}).rename(columns={"revenue": "Cash Inflow"}).reset_index()

monthly_purchases = purchases.groupby(purchases['order_date'].dt.to_period('M')).agg({
    'cost_price': lambda x: (x * purchases.loc[x.index, 'quantity_purchased']).sum()
}).rename(columns={"cost_price": "Cash Outflow"}).reset_index()

cashflow = pd.merge(monthly_sales, monthly_purchases, left_on='sales_date', right_on='order_date', how='outer')
cashflow = cashflow.fillna(0)
cashflow['Net Cash Flow'] = cashflow['Cash Inflow'] - cashflow['Cash Outflow']
cashflow['Month'] = cashflow['sales_date'].astype(str).fillna(cashflow['order_date'].astype(str))

st.subheader("📆 Monthly Cash Flow")
fig = px.bar(
    cashflow,
    x='Month',
    y=['Cash Inflow', 'Cash Outflow', 'Net Cash Flow'],
    barmode='group',
    title='Monthly Cash Flow Summary',
    labels={'value': 'Amount (₹)', 'Month': 'Month'}
)
st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Category-Wise Profitability
# -------------------------
st.subheader("📂 Profit by Category")
category_profit = sales.groupby('category').agg({
    'revenue': 'sum',
    'cost': 'sum',
    'profit': 'sum'
}).reset_index()

fig2 = px.bar(
    category_profit,
    x='category',
    y='profit',
    color='category',
    title='Profitability by Product Category',
    labels={'profit': 'Profit (₹)', 'category': 'Category'}
)
st.plotly_chart(fig2, use_container_width=True)

st.caption("📌 Data visualized from your sales, purchases, and inventory tables.")
