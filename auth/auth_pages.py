# auth/auth_pages.py

import streamlit as st
from .authentication import register_user, login_user, is_logged_in

def registration_page():
    st.title("Register")

    with st.form(key='registration_form'):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        submit_button = st.form_submit_button("Register")

    if submit_button:
        if password == confirm_password:
            success = register_user(username, email, password)
            if success:
                st.success("Registration successful! You can now log in.")
            else:
                st.error("Username or email already exists.")
        else:
            st.error("Passwords do not match.")

def login_page():
    st.title("Login")

    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submit_button = st.form_submit_button("Login")

    if submit_button:
        if login_user(username, password):
            st.success("Login successful!")
            st.session_state['username'] = username
        else:
            st.error("Invalid username or password.")

def protected_page():
    if not is_logged_in():
        st.warning("You need to log in to access this page.")
        login_page()  # Call the login page directly
        return

    st.title("Protected Content")
    st.write("This content is only accessible to logged-in users.")
