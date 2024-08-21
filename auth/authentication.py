# auth/authentication.py
import streamlit as st
from auth.security import hash_password, check_password

# Function to handle user registration
def register_user(username, email, password):
    from auth.database import execute_query  # Lazy import to avoid circular import
    hashed_password = hash_password(password)
    try:
        execute_query('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                      (username, email, hashed_password))
        return True
    except Exception as e:
        st.error(f"Error registering user: {e}")
        return False

# Function to handle user login
def login_user(username, password):
    from auth.database import fetch_one  # Lazy import to avoid circular import
    user = fetch_one('SELECT * FROM users WHERE username = ?', (username,))
    
    if user and check_password(password, user['password']):
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = user['id']
        st.session_state['username'] = user['username']
        return True
    else:
        st.error("Incorrect username or password.")
        return False

# Function to check if a user is logged in
def is_logged_in():
    return st.session_state.get('logged_in', False)

# Function to log out the user
def logout_user():
    st.session_state.clear()  # Clear all session state
    st.success("You have been logged out.")
