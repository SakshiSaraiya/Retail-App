import streamlit as st
import pandas as pd
from db_connector import get_connection

# --- Page Config ---
st.set_page_config(
    page_title="Upload Data | Retail Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }

    .block-container {
        background-color: #F8FAFC;
        padding-top: 2rem;
        color: #1E293B;
    }

    h1 {
        color: #0F172A !important;
        font-weight: 800;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1E293B;
        margin: 2rem 0 1rem;
    }

    .stExpander {
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        margin-bottom: 1.5rem;
    }

    .stButton>button {
        background-color: #0F172A;
        color: white;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.5rem 1.2rem;
    }

    .stButton>button:hover {
        background-color: #1E293B;
    }

    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Upload or Add Inventory Data</h1>", unsafe_allow_html=True)

conn = get_connection()
if conn is None:
    st.stop()

cursor = conn.cursor()

# --- Upload CSV Files Section ---
st.markdown("<div class='section-title'>Upload CSV Files</div>", unsafe_allow_html=True)

product_file = st.file_uploader("Upload Product CSV", type=["csv"])
if product_file:
    df = pd.read_csv(product_file)
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO product (product_id, product_name, category, stock)
                VALUES (%s, %s, %s, %s)
            """, (row['product_id'], row['product_name'], row['category'], row['stock']))
        except Exception as e:
            st.warning(f"Skipped a row due to error: {e}")
    conn.commit()
    st.success("Product data uploaded successfully!")

purchase_file = st.file_uploader("Upload Purchase CSV", type=["csv"])
if purchase_file:
    df = pd.read_csv(purchase_file)
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO purchases (product_id, product_name, category, vendor_name, order_date,
                    quantity_purchased, cost_price, payment_due_date, payment_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (row['product_id'], row['product_name'], row['category'], row['vendor_name'],
                  row['order_date'], row['quantity_purchased'], row['cost_price'],
                  row['payment_due_date'], row['payment_status']))
        except Exception as e:
            st.warning(f"Skipped a row due to error: {e}")
    conn.commit()
    st.success("Purchase data uploaded successfully!")

sales_file = st.file_uploader("Upload Sales CSV", type=["csv"])
if sales_file:
    df = pd.read_csv(sales_file)
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO sales (sale_id, product_id, selling_price, quantity_sold, sales_date,
                    shipped_status, payment_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (row['sale_id'], row['product_id'], row['selling_price'], row['quantity_sold'],
                  row['sales_date'], row['shipped_status'], row['payment_status']))
        except Exception as e:
            st.warning(f"Skipped a row due to error: {e}")
    conn.commit()
    st.success("Sales data uploaded successfully!")

# --- Add Manually ---
st.markdown("<div class='section-title'>Add Data Manually</div>", unsafe_allow_html=True)

# --- Add Purchase ---
with st.expander("➕ Add New Purchase", expanded=False):
    with st.form("add_purchase_form"):
        product_id = st.text_input("Product ID")
        product_name = st.text_input("Product Name")
        category = st.text_input("Category")
        vendor_name = st.text_input("Vendor Name")
        order_date = st.date_input("Order Date")
        quantity_purchased = st.number_input("Quantity Purchased", min_value=1)
        cost_price = st.number_input("Cost Price", min_value=0.0)
        payment_due_date = st.date_input("Payment Due Date")
        payment_status = st.selectbox("Payment Status", ["Pending", "Paid", "Overdue"])
        submit = st.form_submit_button("Add Purchase")
        if submit:
            try:
                cursor.execute("""
                    INSERT INTO purchases (product_id, product_name, category, vendor_name, order_date,
                        quantity_purchased, cost_price, payment_due_date, payment_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (product_id, product_name, category, vendor_name, order_date,
                      quantity_purchased, cost_price, payment_due_date, payment_status))
                conn.commit()
                st.success("Purchase added successfully!")
            except Exception as e:
                st.error("Error inserting purchase.")
                st.code(str(e))

# --- Add Product ---
with st.expander("➕ Add New Product", expanded=False):
    with st.form("add_product_form"):
        product_id = st.text_input("Product ID")
        product_name = st.text_input("Product Name")
        category = st.text_input("Category")
        stock = st.number_input("Stock Quantity", min_value=0)
        submit = st.form_submit_button("Add Product")
        if submit:
            try:
                cursor.execute("SELECT 1 FROM product WHERE product_id = %s", (product_id,))
                if cursor.fetchone():
                    st.error("Product ID already exists.")
                else:
                    cursor.execute("""
                        INSERT INTO product (product_id, product_name, category, stock)
                        VALUES (%s, %s, %s, %s)
                    """, (product_id, product_name, category, stock))
                    conn.commit()
                    st.success("Product added successfully!")
            except Exception as e:
                st.error("Error inserting product.")
                st.code(str(e))

# --- Add Sale ---
with st.expander("➕ Add New Sale", expanded=False):
    with st.form("add_sale_form"):
        sale_id = st.number_input("Sale ID", min_value=1)
        product_id = st.text_input("Product ID")
        selling_price = st.number_input("Selling Price", min_value=0.0)
        quantity_sold = st.number_input("Quantity Sold", min_value=1)
        sales_date = st.date_input("Sales Date")
        shipped_status = st.selectbox("Shipped Status", ["Shipped", "Pending", "Cancelled"])
        payment_status = st.selectbox("Payment Status", ["Received", "Pending"])
        submit = st.form_submit_button("Add Sale")
        if submit:
            try:
                cursor.execute("SELECT 1 FROM sales WHERE sale_id = %s", (sale_id,))
                if cursor.fetchone():
                    st.error("Sale ID already exists.")
                else:
                    cursor.execute("""
                        INSERT INTO sales (sale_id, product_id, selling_price, quantity_sold, sales_date,
                            shipped_status, payment_status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (sale_id, product_id, selling_price, quantity_sold,
                          sales_date, shipped_status, payment_status))
                    conn.commit()
                    st.success("Sale added successfully!")
            except Exception as e:
                st.error("Error inserting sale.")
                st.code(str(e))
