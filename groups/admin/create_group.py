# groups/create_group.py

import streamlit as st
from auth.database import execute_query

def create_group():
    st.subheader("Create a New Group")

    with st.form(key='create_group_form'):
        group_name = st.text_input("Group Name")
        group_description = st.text_area("Group Description")

        submit_button = st.form_submit_button("Create Group")

    if submit_button:
        if group_name:
            user_id = st.session_state['user_id']  # Get the logged-in user's ID
            execute_query('INSERT INTO groups (name, description, user_id) VALUES (?, ?, ?)', 
                          (group_name, group_description, user_id))
            st.success("Group created successfully!")
        else:
            st.error("Group name is required.")
