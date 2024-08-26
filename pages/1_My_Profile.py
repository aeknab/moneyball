# streamlit: My Profile

import streamlit as st
from my_profile.my_profile import display_profile_page

st.set_page_config(page_title="My Profile")
display_profile_page()
