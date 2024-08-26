import streamlit as st
import pandas as pd
from analysis.pie_chart_group import display_group_pie_chart
from analysis.heat_map_group import display_group_heat_map
from analysis.histogram_group import display_matchday_histogram
from analysis.density_plot import display_season_density_plot
from analysis.donut_chart import display_donut_chart
from analysis.confusion_matrix import display_confusion_matrix
from analysis.line_plot import display_line_plot  # Import the line plot function

def display_analysis_section(matchday, rankings_df, matchdays_df):
    # Move the Select Player dropdown directly under the Select Matchday dropdown
    col1, col2 = st.columns([1, 1])  # Adjust the width so both dropdowns are the same length

    with col1:
        # Display the player selection dropdown
        players = sorted(rankings_df['Name'].unique())
        players.insert(0, 'All')  # Add 'All' option at the beginning

        selected_player = st.selectbox("Select Player", players)  # Use a dropdown instead of multiselect

        # If 'All' is selected, we consider all players
        selected_players = players[1:] if selected_player == 'All' else [selected_player]

    # Display the Heat Maps
    display_group_heat_map(matchdays_df, selected_players)

    # Display the Pie Charts
    display_group_pie_chart(matchdays_df, selected_players)

    # Display the Matchday Histogram
    display_matchday_histogram(matchday, rankings_df, selected_players)

    # Display the Season Density Plot
    display_season_density_plot(matchday, rankings_df, selected_players)

    # Display the Donut Chart
    display_donut_chart(matchdays_df, selected_players, matchday)

    # Display the Confusion Matrix
    display_confusion_matrix(matchdays_df, selected_players, matchday)

    # Display the Line Plot
    display_line_plot(matchdays_df, selected_players)
