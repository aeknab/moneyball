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
    # Create a single column for the player selection dropdown
    col1 = st.columns(1)[0]

    with col1:
        # Display the player selection dropdown
        players = sorted(rankings_df['Name'].unique())
        players.insert(0, 'All')  # Add 'All' option at the beginning
        selected_player = st.selectbox("Select Player", players)  # Use a dropdown instead of multiselect

    # Determine which players to display based on the selection
    selected_players = players[1:] if selected_player == 'All' else [selected_player]

    # Section 1: Histogram
    display_matchday_histogram(matchday, rankings_df, selected_players)

    # Section 2: Density Plot
    display_season_density_plot(matchday, rankings_df, selected_players)

    # Section 3: Donut Chart
    display_donut_chart(matchdays_df, selected_players, matchday)

    # Section 4: Confusion Matrix
    display_confusion_matrix(matchdays_df, selected_players, matchday)

    # Section 5: Group Predictions vs. Bundesliga Actual Results Pie Charts (side-by-side)
    display_group_pie_chart(matchdays_df, selected_players)

    # Section 6: Group Predictions Heatmap and Bundesliga Actual Results Heatmap (side-by-side)
    display_group_heat_map(matchdays_df, selected_players)

    # Section 7: Line Plot
    display_line_plot(matchdays_df, selected_players)
