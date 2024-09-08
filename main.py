import streamlit as st
from PIL import Image
from auth.database import initialize_db, execute_query, fetch_one
from groups.groups import display_groups_page

# Set page configuration
st.set_page_config(page_title="Home", page_icon="⚽")

# Initialize the database and ensure the dummy user and group exist
initialize_db()

# Automatically simulate a logged-in user (Dummy User)
if "logged_in" not in st.session_state:
    st.session_state['logged_in'] = True
    st.session_state['user_id'] = 1  # Dummy user ID
    st.session_state['username'] = "DummyUser"  # Dummy username

    # Check if dummy user exists, if not create one
    dummy_user = fetch_one('SELECT * FROM users WHERE id = ?', (1,))
    if not dummy_user:
        execute_query('INSERT INTO users (id, username, email, password) VALUES (1, "DummyUser", "dummy@user.com", "dummy_password")')

    # Check if test group exists, if not create one and add the dummy user to it
    test_group = fetch_one('SELECT * FROM groups WHERE name = "Test Group"')
    if not test_group:
        execute_query('INSERT INTO groups (name, description) VALUES ("Test Group", "A group for testing purposes")')
        group_id = fetch_one('SELECT id FROM groups WHERE name = "Test Group"')['id']
        execute_query('INSERT INTO user_groups (user_id, group_id, is_admin) VALUES (1, ?, 1)', (group_id,))

# Check if the user is logged in
if st.session_state['logged_in']:
    st.sidebar.title("Navigation")
    st.sidebar.write(f"Logged in as {st.session_state.get('username', 'Unknown')}")

    # Logout button (optional, you can remove it if not needed)
    if st.sidebar.button("Logout"):
        st.session_state.clear()  # Clear session state to "log out"
        st.experimental_rerun()

    # Sidebar navigation options
    page = st.sidebar.selectbox("Choose a page", ["Home", "My Groups"])

    if page == "Home":
        
        # Load and display the image
        image = Image.open("data/logos/moneyball/moneyball.png")
        st.image(image, use_column_width=True)

    elif page == "My Groups":
        display_groups_page()

else:
    # This block is skipped because we're automatically logging in the dummy user
    # But kept here for reference and to easily revert later
    col1, col2 = st.columns([1, 1])

    with col1:
        # Load and resize the image using Pillow
        image = Image.open("data/logos/moneyball/moneyball.png")
        st.image(image, use_column_width=True)

    with col2:
        st.title("Login")

        username = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Log In"):
            if login_user(username, password):
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid email or password.")

        if st.button("Create new account"):
            registration_page()

        st.write("[Forgot Password?](#)", unsafe_allow_html=True)