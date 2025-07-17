import streamlit as st
from db_connector import get_connection
import streamlit_authenticator as stauth
import mysql.connector

st.title("🔐 User Registration")

with st.form("register_form"):
    full_name = st.text_input("Full Name")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    submitted = st.form_submit_button("Register")

    if submitted:
        if not (full_name and username and password and confirm_password):
            st.warning("Please fill all the fields.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            hashed_pw = stauth.Hasher([password]).generate()[0]

            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, name, password) VALUES (%s, %s, %s)",
                               (username, full_name, hashed_pw))
                conn.commit()
                st.success("✅ Registered successfully! Please go to the Login page.")
                cursor.close()
                conn.close()
            except mysql.connector.Error as e:
                if "Duplicate entry" in str(e):
                    st.error("❌ Username already taken. Try another one.")
                else:
                    st.error(f"Database error: {e}")
