import streamlit as st
import pandas as pd

from auth.database import fetch_all, execute_query
from groups.groups_season import display_season_section
from groups.groups_matchday import display_matchday_section
from groups.groups_analysis import display_analysis_section
from groups.groups_summary import display_summaries_section

def display_groups_page():
    st.title("My Groups")

    # Check if user_id exists in session_state, if not initialize it
    if 'user_id' not in st.session_state:
        st.warning("User ID not found. Please log in.")
        return  # Stop the execution until user_id is provided

    # Fetch the user's groups from the database
    groups = fetch_all('''
        SELECT g.*, ug.is_admin 
        FROM groups g 
        JOIN user_groups ug ON g.id = ug.group_id 
        WHERE ug.user_id = ?
    ''', (st.session_state['user_id'],))

    if groups:
        # Assume the first group as the selected one since there's only one
        selected_group_name = groups[0]['name']
        selected_group = groups[0]

        # Section Selection with Buttons
        section = st.session_state.get('selected_section', 'Overview')  # Default to Overview

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Overview"):
                section = "Overview"
        with col2:
            if st.button("Matchday"):
                section = "Matchday"
        with col3:
            if st.button("Analysis"):
                section = "Analysis"
        with col4:
            if st.button("Summary"):
                section = "Summary"

        st.session_state['selected_section'] = section

        # Matchday Dropdown - Most recent matchday on top
        matchday = st.selectbox("Select Matchday", options=list(range(1, 35))[::-1])

        # Load the merged_rankings.csv file and merged_matchdays.csv
        rankings_df = pd.read_csv("data/merged_rankings.csv")
        matchdays_df = pd.read_csv("data/merged_matchdays.csv")

        # Display the selected section
        if section == "Overview":
            display_season_section(matchday, rankings_df, matchdays_df)
        elif section == "Matchday":
            display_matchday_section(matchday)
        elif section == "Analysis":
            display_analysis_section(matchday, rankings_df, matchdays_df)
        elif section == "Summary":
            display_summaries_section(matchday, selected_group_name, rankings_df, matchdays_df)
