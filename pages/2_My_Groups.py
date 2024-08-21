# streamlit: My Groups

import streamlit as st
from groups.groups import display_groups_page

st.set_page_config(page_title="My Groups")
display_groups_page()

