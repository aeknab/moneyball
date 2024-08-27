import streamlit as st
import pandas as pd
from analysis.pie_chart_group import display_group_pie_chart
from analysis.heat_map_group import display_group_heat_map
from analysis.confusion_matrix import display_confusion_matrix
from analysis.line_plot import display_line_plot

def display_analysis_section(matchday, rankings_df, matchdays_df):
    # Create a single column for the player selection dropdown
    col1 = st.columns(1)[0]

    with col1:
        # Display the player selection dropdown
        players = sorted(rankings_df['Name'].unique())
        players.insert(0, 'All')  # Add 'All' option at the beginning
        selected_player = st.selectbox("Select Player", players)  # Use a dropdown instead of multiselect

    # Determine which players to display based on the selection
    selected_players = players[1:] if selected_player == 'All' else [selected_player]

    # Section Selection with Buttons
    section = st.session_state.get('selected_analysis_section', 'Pie Chart')  # Default to Pie Chart

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Pie Chart"):
            section = "Pie Chart"
    with col2:
        if st.button("Confusion Matrix"):
            section = "Confusion Matrix"
    with col3:
        if st.button("Heat Map"):
            section = "Heat Map"
    with col4:
        if st.button("Line Plot"):
            section = "Line Plot"

    st.session_state['selected_analysis_section'] = section

    # Display the selected section
    if section == "Pie Chart":
        display_group_pie_chart(matchdays_df, selected_players)
    elif section == "Confusion Matrix":
        display_confusion_matrix(matchdays_df, selected_players, matchday)
    elif section == "Heat Map":
        display_group_heat_map(matchdays_df, selected_players)
    elif section == "Line Plot":
        display_line_plot(matchdays_df, selected_players)