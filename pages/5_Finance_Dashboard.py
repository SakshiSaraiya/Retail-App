import streamlit as st
import pandas as pd
import plotly.express as px
from db_connector import get_connection  # Ensure this returns your MySQL connection object

st.set_page_config(page_title="💰 Finance Dashboard", layout="wide")
st.title("📁 Profit by Category")

st.markdown("### 📈 Profitability by Product Category")

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

# Debugging: Display tables
# st.write("🧾 Products Table", products)
# st.write("🛒 Purchases Table", purchases)
# st.write("💰 Sales Table", sales)

# -------------------------
# Merge and Calculate Profit
# -------------------------
try:
    # Merge sales and products to get category
    sales_products = pd.merge(sales, products, on='product_id', how='left')
    purchases_products = pd.merge(purchases, products, on='product_id', how='left')

    # Calculate total revenue and COGS per category
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

    # Merge and calculate Profit
    profit_df = pd.merge(revenue_per_category, cogs_per_category, on='category', how='outer').fillna(0)
    profit_df['Profit'] = profit_df['Revenue'] - profit_df['COGS']

    if profit_df.empty:
        st.warning("⚠️ No data available to display profitability. Please check sales/purchases.")
    else:
        # Show summary table
        st.dataframe(profit_df, use_container_width=True)

        # Plotly Chart
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
    st.error("❌ Error while calculating or merging data.")
    st.exception(e)

# -------------------------
# Footer Note
# -------------------------
st.markdown("🔖 _Data visualized from your sales, purchases, and inventory tables._")
