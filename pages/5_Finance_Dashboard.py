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
# --- Category Profitability ---
st.subheader("📦 Category-wise Profitability")

# Group sales by category to get Revenue
revenue_by_category = sales.groupby("category")["total_amount"].sum().reset_index()
revenue_by_category.columns = ["Category", "Revenue"]

# Group purchases by category to get COGS
cogs_by_category = purchases.groupby("category")["total_cost"].sum().reset_index()
cogs_by_category.columns = ["Category", "COGS"]

# Merge both
profit_df = pd.merge(revenue_by_category, cogs_by_category, on="Category", how="outer").fillna(0)
profit_df["Profit"] = profit_df["Revenue"] - profit_df["COGS"]
profit_df["Margin (%)"] = round((profit_df["Profit"] / profit_df["Revenue"]) * 100, 2)
profit_df["Margin (%)"] = profit_df["Margin (%)"].replace([np.inf, -np.inf], 0).fillna(0)

# Display
st.dataframe(profit_df.style.format({"Revenue": "₹{:,.2f}", "COGS": "₹{:,.2f}", "Profit": "₹{:,.2f}", "Margin (%)": "{:.2f}%"}))

# Optional: Plot
fig = px.bar(profit_df, x="Category", y="Profit", color="Margin (%)", color_continuous_scale="Bluered", title="Profit by Category")
st.plotly_chart(fig, use_container_width=True)

