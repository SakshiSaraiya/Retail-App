import streamlit as st
from streamlit_lottie import st_lottie
import requests
import streamlit_authenticator as stauth
from db_connector import get_connection
import mysql.connector

# -------------------
# CONFIG
# -------------------
st.set_page_config(page_title="All in One Retail Management", layout="wide")

# -------------------
# Hide sidebar if not logged in
# -------------------
if "user" not in st.session_state:
    hide_sidebar = """
    <style>
    [data-testid="stSidebar"] {display: none;}
    </style>
    """
    st.markdown(hide_sidebar, unsafe_allow_html=True)

# -------------------
# AUTHENTICATION
# -------------------
def fetch_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, name, password FROM users")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def login_form():
    st.title("🔐 Login to Continue")

    users = fetch_users()
    usernames = [row[0] for row in users]
    names = [row[1] for row in users]
    passwords = [row[2] for row in users]

    hashed_passwords = passwords  # Already stored as hashed in DB

    authenticator = stauth.Authenticate(
        credentials={"usernames": {
            usernames[i]: {"name": names[i], "password": hashed_passwords[i]}
            for i in range(len(usernames))
        }},
        cookie_name="retail_app_login",
        key="abcdef",
        cookie_expiry_days=1
    )

    name, authentication_status, username = authenticator.login("Login", "main")

    if authentication_status is False:
        st.error("❌ Invalid username or password.")
    elif authentication_status is None:
        st.warning("👈 Please enter your credentials.")
    elif authentication_status:
        st.session_state["user"] = username
        st.experimental_rerun()

# -------------------
# Lottie Animation Loaders
# -------------------
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# -------------------
# If not logged in → Show login
# -------------------
if "user" not in st.session_state:
    login_form()
    st.stop()  # Prevent loading the rest

# -------------------
# After login → Show full app
# -------------------
inventory_lottie = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_jcikwtux.json")
retail_lottie = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_9cyyl8i4.json")

# --- Custom Background and CSS ---
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(to right, #141e30, #243b55);
            color: white;
        }
        h1, h2, h3, .stMarkdown p {
            color: #f0f0f0;
        }
        .nav-bar {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-bottom: 20px;
        }
        .nav-item {
            font-size: 18px;
            padding: 8px 20px;
            background-color: #1f2937;
            border-radius: 10px;
            color: white;
            text-decoration: none;
        }
        .nav-item:hover {
            background-color: #3b82f6;
            cursor: pointer;
        }
        img {
            border-radius: 12px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title Section ---
st.markdown("<h1 style='text-align:center;'> All in One Retail Management</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px;'>Empowering retailers with real-time insights.</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- Main Layout ---
left_col, right_col = st.columns([1.2, 1])

with left_col:
    st.subheader(" Features:")
    st.markdown("""
    - 📋 Inventory: Track stock levels, product variations, and categories.
    - 📈 Sales: View product performance, trends, and orders.
    - 📥 Purchases: Manage vendor performance and payment schedules.
    """)

    st.subheader("Get Started:")
    st.markdown("""
    1. Go to the Upload or Add Data page.
    2. Explore dashboards through the sidebar.
    3. Monitor trends, alerts, and inventory health — all in one place!
    """)

    st.subheader("⚙ Built With:")
    st.markdown("- Python + Streamlit\n- 🛢 MySQL\n- Realtime Dashboards")

    st.markdown("###  Quick Navigation:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Upload Data"):
            st.switch_page("pages/0_upload_data.py")
    with col2:
        if st.button("📊 View Inventory"):
            st.switch_page("pages/1_Home.py")

with right_col:
    st_lottie(inventory_lottie, height=250, key="inventory_anim")
    st_lottie(retail_lottie, height=250, key="retail_anim")

# --- Footer ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center;'>
    🔒 Secure | ⚡ Fast | 🎯 Accurate<br>
    <span style='font-size:12px;'>Built by Sakshi Saraiya & Chirag Thakkar</span>
</div>
""", unsafe_allow_html=True)
