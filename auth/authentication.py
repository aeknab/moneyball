import streamlit as st
from auth.security import hash_password, check_password
from auth.database import execute_query, fetch_one  # Import execute_query and fetch_one here

# Function to handle user registration
def register_user(username, email, password):
    hashed_password = hash_password(password)
    try:
        execute_query('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                      (username, email, hashed_password))
        return True
    except Exception as e:
        st.error(f"Error registering user: {e}")
        return False

# Function to handle user login
def login_user(email, password):
    user = fetch_one('SELECT * FROM users WHERE email = ?', (email,))
    
    if user and check_password(password, user['password']):
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = user['id']
        st.session_state['username'] = user['username']
        return True
    else:
        st.error("Incorrect email or password.")
        return False

# Function to check if a user is logged in
def is_logged_in():
    return st.session_state.get('logged_in', False)

# Function to log out the user
def logout_user():
    st.session_state.clear()  # Clear all session state
    st.success("You have been logged out.")
