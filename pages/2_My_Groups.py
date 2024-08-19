# streamlit: My Groups

import streamlit as st
from modules.groups import display_groups_page

st.set_page_config(page_title="My Groups")
st.title("My Groups")
display_groups_page()
