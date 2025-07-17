import streamlit as st
import pandas as pd
import plotly.express as px
from db_connector import get_connection

st.set_page_config(page_title="💰 Finance Dashboard", layout="wide")
st.title("📁 Financial Health Dashboard")

st.markdown("### 📊 Financial Summary")

# -------------------------
# Connect to Database
# -------------------------
conn = get_connection()

# -------------------------
# Load Data
# -------------------------
try:
    products = pd.read_sql("SELECT * FROM inventory", conn)
    purchases = pd.read_sql("SELECT * FROM purchases", conn)
    sales = pd.read_sql("SELECT * FROM sales", conn)
except Exception as e:
    st.error("❌ Failed to fetch data from the database.")
    st.exception(e)
    st.stop()

# -------------------------
# Merge and Financial Metrics
# -------------------------
try:
    # Merge sales with product to get cost info
    sales_products = pd.merge(sales, products, on='product_id', how='left')
    purchases_products = pd.merge(purchases, products, on='product_id', how='left')

    # Revenue = selling_price * quantity_sold
    total_revenue = (sales_products['selling_price'] * sales_products['quantity_sold']).sum()

    # COGS = cost_price * quantity_purchased
    total_cogs = (purchases_products['cost_price'] * purchases_products['quantity_purchased']).sum()

    # Gross Profit
    gross_profit = total_revenue - total_cogs

    # Margin %
    gross_margin_pct = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

    # Display Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💵 Total Revenue", f"₹{total_revenue:,.2f}")
    col2.metric("💰 COGS", f"₹{total_cogs:,.2f}")
    col3.metric("📈 Gross Profit", f"₹{gross_profit:,.2f}")
    col4.metric("📊 Gross Margin %", f"{gross_margin_pct:.2f}%")

except Exception as e:
    st.error("❌ Failed to compute financial metrics.")
    st.exception(e)

# -------------------------
# Profit by Category Chart
# -------------------------
st.markdown("### 🧮 Profitability by Product Category")

try:
    revenue_per_category = (
        sales_products
        .groupby('category')
        .apply(lambda df: (df['selling_price'] * df['quantity_sold']).sum())
        .reset_index(name='Revenue')
    )

    cogs_per_category = (
        purchases_products
        .groupby('category')
        .apply(lambda df: (df['cost_price'] * df['quantity_purchased']).sum())
        .reset_index(name='COGS')
    )

    profit_df = pd.merge(revenue_per_category, cogs_per_category, on='category', how='outer').fillna(0)
    profit_df['Profit'] = profit_df['Revenue'] - profit_df['COGS']

    if profit_df.empty:
        st.warning("⚠️ No data available to display category-wise profitability.")
    else:
        st.dataframe(profit_df, use_container_width=True)

        fig = px.bar(
            profit_df,
            x="category",
            y="Profit",
            title="Profitability by Product Category",
            labels={"Profit": "Profit (₹)", "category": "Category"},
            color="Profit",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error("❌ Error in category profitability section.")
    st.exception(e)

st.markdown("🔖 _All metrics derived from sales, purchases, and inventory tables._")
