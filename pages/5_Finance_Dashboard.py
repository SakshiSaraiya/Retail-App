import streamlit as st 
import pandas as pd
import plotly.express as px
import numpy as np
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
    products = pd.read_sql("SELECT * FROM product", conn)
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
    sales_products = pd.merge(sales, products, on='product_id', how='left')

    total_revenue = (sales_products['selling_price'] * sales_products['quantity_sold']).sum()
    total_cogs = (sales_products['cost_price'] * sales_products['quantity_sold']).sum()
    gross_profit = total_revenue - total_cogs
    gross_margin_pct = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

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
st.subheader("📦 Category-wise Profitability")

try:
    # Merge sales with purchases to get category and cost info
    sales_with_cost = pd.merge(
        sales,
        purchases[['product_id', 'cost_price', 'category']],
        on='product_id',
        how='left'
    )

    sales_with_cost["revenue"] = sales_with_cost["quantity_sold"] * sales_with_cost["selling_price"]
    sales_with_cost["cogs"] = sales_with_cost["quantity_sold"] * sales_with_cost["cost_price"]

    # Aggregate revenue and cost by category
    revenue_by_category = sales_with_cost.groupby("category")["revenue"].sum().reset_index()
    cogs_by_category = sales_with_cost.groupby("category")["cogs"].sum().reset_index()

    # Merge Revenue and COGS
    profit_df = pd.merge(revenue_by_category, cogs_by_category, on="category", how="outer").fillna(0)
    profit_df.columns = ["Category", "Revenue", "COGS"]
    profit_df["Profit"] = profit_df["Revenue"] - profit_df["COGS"]
    profit_df["Margin (%)"] = np.where(
        profit_df["Revenue"] > 0,
        round((profit_df["Profit"] / profit_df["Revenue"]) * 100, 2),
        0
    )

    # Display Dataframe
    st.dataframe(
        profit_df.style.format({
            "Revenue": "₹{:,.2f}",
            "COGS": "₹{:,.2f}",
            "Profit": "₹{:,.2f}",
            "Margin (%)": "{:.2f}%"
        })
    )

    # Plot
    fig = px.bar(
        profit_df,
        x="Category",
        y="Profit",
        color="Margin (%)",
        color_continuous_scale="Bluered",
        title="Profit by Category (Based on Sold Quantities)"
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error("❌ Error in category profitability section.")
    st.exception(e)
