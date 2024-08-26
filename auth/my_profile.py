import streamlit as st
from auth.database import fetch_one, execute_query

# Function to display the user profile
def display_profile(user_id):
    user = fetch_one('SELECT * FROM users WHERE id = ?', (user_id,))
    
    if user:
        st.subheader(f"Profile: {user['username']}")
        st.write(f"Email: {user['email']}")
        
        if user['profile_picture']:
            st.image(user['profile_picture'], width=150)
        else:
            st.write("No profile picture uploaded.")
    else:
        st.error("User not found.")

# Function to edit and update the user profile
def edit_profile(user_id):
    user = fetch_one('SELECT * FROM users WHERE id = ?', (user_id,))
    
    if user:
        new_email = st.text_input("Email", value=user['email'])
        profile_picture = st.file_uploader("Upload a profile picture", type=["jpg", "png"])
        
        if st.button("Save Changes"):
            if profile_picture:
                profile_picture_data = profile_picture.read()
            else:
                profile_picture_data = user['profile_picture']
            
            execute_query('UPDATE users SET email = ?, profile_picture = ? WHERE id = ?', 
                          (new_email, profile_picture_data, user_id))
            st.success("Profile updated successfully.")
    else:
        st.error("User not found.")
