import streamlit as st
import pandas as pd
from modules.data_loader import load_data
from modules.match_preview import display_match_preview
from modules.form_guide_last_5 import display_form_guide_section
from modules.form_guide_last_10 import plot_last_10_meetings
from modules.form_guide_season import display_donut_charts_side_by_side
from modules.league_table import display_league_tables
from modules.bump_chart import display_bump_chart
from modules.pie_chart import display_pie_chart
from modules.heat_map import display_heat_map
from modules.histogram import display_histogram

def display_bundesliga_page():
    # Load data once, to be used across the app
    df = load_data()

    # Load color codes
    color_codes_df = pd.read_csv("data/color_codes.csv")

    # Streamlit app layout
    st.title("Moneyball Dashboard")

    # Bundesliga Section
    selected_season, selected_matchday, selected_match, df_matches = display_match_preview(df)

    # Ensure selections are made before proceeding
    if selected_season != '--' and selected_matchday != '--' and selected_match != '--':
        selected_match_row = df_matches[
            df_matches.apply(lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1) == selected_match
        ].iloc[0]

        home_team_tag = selected_match_row['Home Tag']
        away_team_tag = selected_match_row['Away Tag']

        # Display the form guide sections
        display_form_guide_section(df, selected_season, selected_matchday, selected_match, df_matches)
        
        # Display the season form guide donut charts
        display_donut_charts_side_by_side(selected_match_row['Home Team'], selected_match_row['Away Team'], home_team_tag, away_team_tag, selected_matchday, df[df['Season'] == selected_season])

        # Display the last 10 meetings
        plot_last_10_meetings(df, home_team_tag, away_team_tag, color_codes_df, selected_matchday, selected_season)

        # Display the league tables
        display_league_tables(df, selected_season, selected_matchday, "Full Table", color_codes_df)

        # Season Data Section
        st.header("Season Data")

        # Define the initial state for the selected visualization
        if "selected_viz" not in st.session_state:
            st.session_state.selected_viz = "Bump Chart"

        # Create buttons and update the selected visualization
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Bump Chart"):
                st.session_state.selected_viz = "Bump Chart"
        with col2:
            if st.button("Pie Chart"):
                st.session_state.selected_viz = "Pie Chart"
        with col3:
            if st.button("Heat Map"):
                st.session_state.selected_viz = "Heat Map"
        with col4:
            if st.button("Histogram"):
                st.session_state.selected_viz = "Histogram"

        # Display the selected visualization
        if st.session_state.selected_viz == "Bump Chart":
            display_bump_chart(df, selected_season, selected_matchday, color_codes_df)
        elif st.session_state.selected_viz == "Pie Chart":
            display_pie_chart(df, selected_season, selected_matchday, color_codes_df)
        elif st.session_state.selected_viz == "Heat Map":
            display_heat_map(df, selected_season, selected_matchday, color_codes_df)
        elif st.session_state.selected_viz == "Histogram":
            display_histogram(df, selected_season, selected_matchday, color_codes_df)

    else:
        st.write("Please select a season, matchday, and fixture.")
