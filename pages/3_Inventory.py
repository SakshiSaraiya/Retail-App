import streamlit as st 
import pandas as pd
import plotly.express as px
from db_connector import get_connection

st.set_page_config(page_title="Inventory", layout="wide")

# -------------------------
# Custom Styling
# -------------------------
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #1E293B;
    }

    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
        font-size: 0.95rem;
    }

    .metric-card {
        background-color: #1E293B;
        color: #FFFFFF;
        padding: 0.7rem 1rem;
        border-radius: 0.75rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 1rem;
        min-height: 90px;
    }
    .metric-card h4 {
        font-size: 1.05rem;
        margin-bottom: 0.25rem;
        color: #CBD5E1;
    }
    .metric-card h2 {
        font-size: 1.9rem;
        margin: 0;
        font-weight: 700;
        color: #FACC15;
    }
    .dataframe tbody td {
        font-size: 0.95rem;
        color: #1F2937;
    }
    .dataframe thead th {
        background-color: #CBD5E1;
        font-weight: bold;
        color: #1E293B;
        font-size: 0.95rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h2 style='margin-bottom: 1rem;'>Inventory Overview</h2>
""", unsafe_allow_html=True)

conn = get_connection()

try:
    purchases = pd.read_sql("SELECT product_id, product_name, category, quantity_purchased, cost_price FROM purchases", conn)
    sales = pd.read_sql("SELECT product_id, quantity_sold, selling_price FROM sales", conn)
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

purchases['product_id'] = purchases['product_id'].astype(str).str.strip().str.upper()
sales['product_id'] = sales['product_id'].astype(str).str.strip().str.upper()

purchase_agg = purchases.groupby(['product_id', 'product_name', 'category']).agg({
    'quantity_purchased': 'sum',
    'cost_price': 'mean'
}).reset_index()

sales_agg = sales.groupby('product_id').agg({
    'quantity_sold': 'sum',
    'selling_price': 'mean'
}).reset_index()

inventory_df = purchase_agg.merge(sales_agg, on='product_id', how='left')

inventory_df['quantity_sold'] = inventory_df['quantity_sold'].fillna(0)
inventory_df['selling_price'] = inventory_df['selling_price'].fillna(0)

inventory_df['live_stock'] = inventory_df['quantity_purchased'] - inventory_df['quantity_sold']
inventory_df['stock_value'] = inventory_df['live_stock'] * inventory_df['cost_price']
inventory_df['potential_revenue'] = inventory_df['live_stock'] * inventory_df['selling_price']
inventory_df['profit_margin'] = inventory_df['selling_price'] - inventory_df['cost_price']
inventory_df['total_profit'] = inventory_df['profit_margin'] * inventory_df['live_stock']

inventory_df.rename(columns={
    'product_name': 'name',
    'category': 'Category',
    'cost_price': 'Cost Price',
    'selling_price': 'Selling Price'
}, inplace=True)

st.sidebar.header("Filter Inventory")
categories = inventory_df['Category'].dropna().unique()
selected_category = st.sidebar.multiselect("Category", categories, default=list(categories))
search_term = st.sidebar.text_input("Search Product")

filtered = inventory_df[inventory_df['Category'].isin(selected_category)]
if search_term:
    filtered = filtered[filtered['name'].str.contains(search_term, case=False)]

st.markdown("<h4 style='margin-top:2rem;'>Key Metrics</h4>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Total Live Stock</h4>
            <h2>{int(filtered['live_stock'].sum())}</h2>
        </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Stock Value</h4>
            <h2>₹ {filtered['stock_value'].sum():,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Revenue Potential</h4>
            <h2>₹ {filtered['potential_revenue'].sum():,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
        <div class='metric-card'>
            <h4>Avg. Margin</h4>
            <h2>₹ {filtered['profit_margin'].mean():.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

st.markdown("### 📋 Product List (Live Stock)")
st.dataframe(filtered[['product_id', 'name', 'Category', 'Cost Price', 'Selling Price', 'live_stock', 'stock_value']], use_container_width=True)

low_stock = filtered[filtered['live_stock'] < 10]

if not low_stock.empty:
    st.markdown("### ⚠️ Low Stock Alerts")
    st.markdown("""
        <div style='background-color:#F87171;padding:10px;border-radius:5px;color:white;font-weight:600;'>
            ⚠️ {0} product(s) are low on stock
        </div>
    """.format(low_stock.shape[0]), unsafe_allow_html=True)
    st.dataframe(low_stock[['product_id', 'name', 'Category', 'live_stock']], use_container_width=True)
else:
    st.success("✅ All filtered products are well stocked.")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    category_value = filtered.groupby('Category')['stock_value'].sum().reset_index()
    fig1 = px.pie(category_value, names='Category', values='stock_value',
                 title="Inventory Value by Category", hole=0.45,
                 color_discrete_sequence=px.colors.sequential.RdBu)
    fig1.update_layout(showlegend=True, plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    top_profit = filtered.sort_values(by='total_profit', ascending=False).head(10)
    fig2 = px.bar(top_profit, x='name', y='total_profit', color='profit_margin',
                 title="Top Products by Profit Potential",
                 color_continuous_scale='viridis')
    fig2.update_layout(xaxis_title="Product", yaxis_title="Profit", showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
top_stock = st.slider("Top N Products by Stock", 5, 20, 10)
stock_bar = px.bar(
    filtered.sort_values(by='live_stock', ascending=False).head(top_stock),
    x='name', y='live_stock',
    title=f"Top {top_stock} Products by Live Stock",
    color='live_stock',
    color_continuous_scale='sunsetdark'
)
stock_bar.update_layout(xaxis_title="Product", yaxis_title="Live Stock", showlegend=False)
st.plotly_chart(stock_bar, use_container_width=True)
