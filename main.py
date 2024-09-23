import streamlit as st
from PIL import Image
from auth.database import initialize_db, execute_query, fetch_one
from groups.groups import display_groups_page
from bundesliga.bundesliga import display_bundesliga_page

# Set page configuration
st.set_page_config(page_title="Home", page_icon="⚽")

# Initialize the database
initialize_db()

# Automatically simulate a logged-in user (Dummy User)
if "logged_in" not in st.session_state:
    st.session_state['logged_in'] = True
    st.session_state['user_id'] = 1  # Dummy user ID
    st.session_state['username'] = "DummyUser"

    # Check if dummy user exists
    dummy_user = fetch_one('SELECT * FROM users WHERE id = ?', (1,))
    if not dummy_user:
        execute_query(
            'INSERT INTO users (id, username, email, password) VALUES (?, ?, ?, ?)',
            (1, "DummyUser", "dummy@user.com", "dummy_password")
        )

    # Check if test group exists
    test_group = fetch_one('SELECT * FROM groups WHERE name = ?', ("Test Group",))
    if not test_group:
        execute_query(
            'INSERT INTO groups (name, description) VALUES (?, ?)',
            ("Test Group", "A group for testing purposes")
        )
        group_id = fetch_one('SELECT id FROM groups WHERE name = ?', ("Test Group",))['id']
        execute_query(
            'INSERT INTO user_groups (user_id, group_id, is_admin) VALUES (?, ?, ?)',
            (1, group_id, 1)
        )

# Function to display the home image
def display_home_image():
    image = Image.open("data/logos/moneyball/moneyball.png")
    st.image(image, use_column_width=True)

# Function to handle the "Just the Tipp" page
def display_just_the_tipp():
    display_groups_page()  # This will call the existing My Groups display logic

# Function to display flag emojis
def display_flag_emoji(flag):
    st.markdown(f"<h1 style='text-align:center;'>{flag}</h1>", unsafe_allow_html=True)

# Check if the user is logged in
if st.session_state['logged_in']:
    # Chained selectbox for the primary menu with "--" as the default option
    primary_menu = st.sidebar.selectbox("Menu", ["--", "Home", "My Groups", "Leagues Data"])

    # Define secondary options based on the primary menu selection
    if primary_menu == "Home":
        secondary_menu = st.sidebar.selectbox("Select an option", ["--", "My Profile", "Account Settings"])

        if secondary_menu == "My Profile":
            st.title("My Profile")
            st.write("Profile details and settings go here.")

        elif secondary_menu == "Account Settings":
            st.title("Account Settings")
            st.write("Account settings and preferences go here.")

    elif primary_menu == "My Groups":
        secondary_menu = st.sidebar.selectbox("Select a group", ["--", "Just the Tipp", "Schlandschaft", "Create Group"])

        if secondary_menu == "Just the Tipp":
            display_just_the_tipp()

        elif secondary_menu == "Schlandschaft":
            display_flag_emoji("🇩🇪")  # German flag emoji

        elif secondary_menu == "Create Group":
            display_flag_emoji("🇺🇸")  # American flag emoji

    elif primary_menu == "Leagues Data":  # Renamed from Bundesliga
        secondary_menu = st.sidebar.selectbox("Select a league", ["--", "Bundesliga", "Premier League", "Champions League"])

        if secondary_menu == "Bundesliga":
            try:
                display_bundesliga_page()  # Call the function to display Bundesliga page
            except Exception as e:
                st.error(f"An error occurred: {e}")

        elif secondary_menu == "Premier League":
            display_flag_emoji("🏴")  # England flag emoji

        elif secondary_menu == "Champions League":
            display_flag_emoji("🇪🇺")  # European Union flag emoji

    # If no selection is made, display the home image
    if primary_menu == "--" or secondary_menu == "--":
        display_home_image()

    # Divider for better UX (optional)
    st.sidebar.markdown("---")

    # Now display the login/logout section after the navigation
    st.sidebar.write(f"Logged in as {st.session_state.get('username', 'Unknown')}")

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.clear()  # Clear session state to "log out"
        st.experimental_rerun()

else:
    # Login logic here
    col1, col2 = st.columns([1, 1])

    with col1:
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