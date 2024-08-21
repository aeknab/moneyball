# streamlit: Home

import streamlit as st
from PIL import Image
from auth.database import initialize_db
from auth.auth_pages import registration_page, login_page, protected_page
from groups.groups import display_groups_page
from auth.authentication import is_logged_in, logout_user

# Set page configuration
st.set_page_config(page_title="Home", page_icon="⚽")

# Initialize the database
initialize_db()

# Sidebar Navigation
st.sidebar.title("Navigation")

if is_logged_in():
    st.sidebar.write(f"Logged in as {st.session_state.get('username', 'Unknown')}")
    
    if st.sidebar.button("Logout"):
        logout_user()
        st.experimental_rerun()  # Refresh the page after logging out
    
    page = st.sidebar.selectbox("Choose a page", ["Home", "Protected Page", "My Groups"])

    if page == "Home":
        st.title("Welcome to the App")
    elif page == "Protected Page":
        protected_page()
    elif page == "My Groups":
        display_groups_page()

else:
    page = st.sidebar.selectbox("Choose a page", ["Home", "Register", "Login"])

    if page == "Home":
        st.title("Welcome to the App")
    elif page == "Register":
        registration_page()
    elif page == "Login":
        login_page()

# Load and crop the image using Pillow
image = Image.open("data/logos/moneyball/moneyball.png")
cropped_image = image.crop(image.getbbox())  # Crop out unnecessary space

# CSS to center the image and text
st.markdown(
    """
    <style>
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: -150px; /* Adjust this value to move the logo higher */
    }
    .centered-text {
        display: flex;
        justify-content: center;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Start the centered content
st.markdown('<div class="centered">', unsafe_allow_html=True)

# Display the cropped image with a larger size
st.image(cropped_image, use_column_width=False, width=600)

# End the centered content
st.markdown('</div>', unsafe_allow_html=True)