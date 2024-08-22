import streamlit as st
from auth.database import execute_query, fetch_one

def validate_invite_code(group_id, invite_code):
    # Example logic to validate invite code, adjust as needed
    invite = fetch_one('SELECT * FROM group_invites WHERE group_id = ? AND invite_code = ?', (group_id, invite_code))
    return invite is not None

def join_group_via_invite(group_id, invite_code):
    try:
        if validate_invite_code(group_id, invite_code):
            execute_query('INSERT INTO user_groups (user_id, group_id, is_admin) VALUES (?, ?, 0)', 
                          (st.session_state['user_id'], group_id))
            st.success("You have successfully joined the group!")
        else:
            st.error("Invalid invite code.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
