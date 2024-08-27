import streamlit as st
import pandas as pd
from analysis.pie_chart_group import display_group_pie_chart
from analysis.heat_map_group import display_group_heat_map
from analysis.histogram_group import display_matchday_histogram
from analysis.density_plot import display_season_density_plot
from analysis.donut_chart import display_donut_chart
from analysis.confusion_matrix import display_confusion_matrix
from analysis.line_plot import display_line_plot

def display_analysis_section(matchday, rankings_df, matchdays_df):
    
    # Display the player selection dropdown
    players = sorted(rankings_df['Name'].unique())
    players.insert(0, 'All')  # Add 'All' option at the beginning
    selected_player = st.selectbox("Select Player", players)  # Use a dropdown instead of multiselect

    # Determine which players to display based on the selection
    selected_players = players[1:] if selected_player == 'All' else [selected_player]

    # Section 1: Histogram and Density Plot
    col1, col2 = st.columns(2)
    with col1:
        display_matchday_histogram(matchday, rankings_df, selected_players)
    with col2:
        display_season_density_plot(matchday, rankings_df, selected_players)

    # Section 2: Donut Chart and Confusion Matrix
    col1, col2 = st.columns(2)
    with col1:
        display_donut_chart(matchdays_df, selected_players, matchday)
    with col2:
        display_confusion_matrix(matchdays_df, selected_players, matchday)

    # Section 3: Group Predictions vs. Bundesliga Actual Results Pie Charts
    display_group_pie_chart(matchdays_df, selected_players)

    # Section 4: Group Predictions Heatmap and Bundesliga Actual Results Heatmap
    display_group_heat_map(matchdays_df, selected_players)

    # Section 5: Line Plot (Full width)
    display_line_plot(matchdays_df, selected_players)
