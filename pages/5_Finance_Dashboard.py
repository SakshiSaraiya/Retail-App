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
    sales_products = pd.merge(sales, purchases, on='product_id', how='left')

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

# -------------------------
# Inventory Holding Cost & DIO
# -------------------------
st.subheader("🏬 Inventory Holding Cost & Efficiency")

try:
    # Merge purchases and sales to compute current inventory
    inventory_df = pd.merge(purchases, sales[['product_id', 'quantity_sold']], on='product_id', how='left')
    inventory_df['quantity_sold'] = inventory_df['quantity_sold'].fillna(0)

    # Current Inventory = Purchased - Sold
    inventory_df['quantity_remaining'] = inventory_df['quantity_purchased'] - inventory_df['quantity_sold']
    inventory_df['inventory_value'] = inventory_df['quantity_remaining'] * inventory_df['cost_price']

    # Total inventory value
    total_inventory_value = inventory_df['inventory_value'].sum()

    # Holding cost rate input
    holding_cost_rate = st.slider("🏷️ Monthly Holding Cost Rate (% of inventory value)", min_value=0.0, max_value=10.0, value=2.0, step=0.1)
    monthly_holding_cost = (holding_cost_rate / 100) * total_inventory_value

    # Calculate Average Inventory (simplified as 50% of current inventory)
    average_inventory_value = total_inventory_value / 2

    # Total COGS for DIO
    total_cogs = (purchases['cost_price'] * purchases['quantity_purchased']).sum()

    # Date range for sales period
    if not sales.empty and 'sale_date' in sales.columns:
        sales['sale_date'] = pd.to_datetime(sales['sale_date'])
        date_range_days = (sales['sale_date'].max() - sales['sale_date'].min()).days or 1
    else:
        date_range_days = 30  # fallback

    # DIO Calculation
    dio = (average_inventory_value / total_cogs) * date_range_days if total_cogs > 0 else 0

    # Display Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Current Inventory Value", f"₹{total_inventory_value:,.2f}")
    col2.metric("📉 Monthly Holding Cost", f"₹{monthly_holding_cost:,.2f}")
    col3.metric("📅 Days Inventory Outstanding (DIO)", f"{dio:.1f} days")

except Exception as e:
    st.error("❌ Error calculating inventory holding cost or DIO.")
    st.exception(e)

# -------------------------
# Supplier Payment Simulation
# -------------------------
st.subheader("🤝 Supplier Payment Simulation")

try:
    if 'order_date' not in purchases.columns:
        st.warning("⚠️ 'order_date' column not found in purchases table.")
    else:
        purchases['order_date'] = pd.to_datetime(purchases['order_date'])

        # Payment Terms Slider
        payment_days = st.slider("📆 Simulate Supplier Payment Terms (in days)", 0, 120, 30, step=5)

        # Today's date
        today = pd.to_datetime("today")

        # Add due_date and check if overdue
        purchases['due_date'] = purchases['order_date'] + pd.to_timedelta(payment_days, unit='D')
        purchases['outstanding_amount'] = purchases['quantity_purchased'] * purchases['cost_price']
        purchases['status'] = np.where(purchases['due_date'] < today, "Overdue", "Pending")

        # Metrics
        total_outstanding = purchases['outstanding_amount'].sum()
        overdue_amount = purchases[purchases['status'] == "Overdue"]['outstanding_amount'].sum()
        pending_amount = purchases[purchases['status'] == "Pending"]['outstanding_amount'].sum()

        # Display Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("💸 Total Payable (Simulated)", f"₹{total_outstanding:,.2f}")
        col2.metric("⚠️ Overdue Amount", f"₹{overdue_amount:,.2f}")
        col3.metric("⏳ Pending (Not Yet Due)", f"₹{pending_amount:,.2f}")

        # Optional: Visual
        fig = px.pie(
            purchases,
            names='status',
            values='outstanding_amount',
            title='💰 Payable Breakdown by Status'
        )
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error("❌ Error in Supplier Payment Simulation section.")
    st.exception(e)
