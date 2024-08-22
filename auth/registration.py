import streamlit as st
from auth.security import hash_password
from auth.database import execute_query

def register_user(email, password):
    hashed_password = hash_password(password)
    try:
        execute_query('INSERT INTO users (email, password) VALUES (?, ?)', 
                      (email, hashed_password))
        return True
    except Exception as e:
        st.error(f"Error registering user: {e}")
        return False

def registration_page():
    st.subheader("Create a New Account")
    
    # Only ask for email and password during registration
    email = st.text_input("Email", key="register_email")
    password = st.text_input("Password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")

    if st.button("Register"):
        if password == confirm_password:
            if register_user(email, password):
                st.success("Registration successful! You can now log in.")
            else:
                st.error("Registration failed.")
        else:
            st.error("Passwords do not match.")
