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
from modules.first_and_second import filter_leg_matches, calculate_leg_points, plot_leg_table
from modules.cross_table import display_cross_table_view
from modules.home_away import filter_home_away_matches, calculate_home_away_points, plot_home_away_table

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

        # League Table Section with Buttons
        st.subheader("League Table")

        # Create four buttons for different views with unique keys
        col1, col2, col3, col4 = st.columns(4)
        if "selected_view" not in st.session_state:
            st.session_state.selected_view = "Full Table"

        with col1:
            if st.button("Full Table", key="full_table_button"):
                st.session_state.selected_view = "Full Table"
        with col2:
            if st.button("Home/Away Table", key="home_away_table_button"):
                st.session_state.selected_view = "Home/Away Table"
        with col3:
            if st.button("1st/2nd Leg Table", key="first_second_leg_table_button"):
                st.session_state.selected_view = "1st/2nd Leg Table"
        with col4:
            if st.button("Cross Table", key="cross_table_button"):
                st.session_state.selected_view = "Cross Table"

        # Display the selected table
        if st.session_state.selected_view == "Full Table":
            display_league_tables(df, selected_season, selected_matchday, "Full Table", color_codes_df)
        elif st.session_state.selected_view == "Home/Away Table":
            # Display Home and Away tables one after the other
            st.subheader("Home Table")
            df_filtered = filter_home_away_matches(df, selected_season, selected_matchday)
            df_home_points = calculate_home_away_points(df_filtered, home_away='home')
            home_fig = plot_home_away_table(df_home_points, f'Home Table After Matchday {selected_matchday} ({selected_season})', color_codes_df, home_away='home')
            st.plotly_chart(home_fig, use_container_width=True)

            st.subheader("Away Table")
            df_away_points = calculate_home_away_points(df_filtered, home_away='away')
            away_fig = plot_home_away_table(df_away_points, f'Away Table After Matchday {selected_matchday} ({selected_season})', color_codes_df, home_away='away')
            st.plotly_chart(away_fig, use_container_width=True)

        elif st.session_state.selected_view == "1st/2nd Leg Table":
            # 1st Leg Table
            st.subheader("1st Leg Table")
            df_leg_1 = filter_leg_matches(df, selected_season, leg='1st', matchday=selected_matchday)
            if df_leg_1.empty:
                st.write("No available data yet.")
            else:
                df_leg_1_points = calculate_leg_points(df_leg_1)
                leg_1_fig = plot_leg_table(df_leg_1_points, f'1st Leg Table After Matchday {selected_matchday} ({selected_season})', color_codes_df)
                st.plotly_chart(leg_1_fig, use_container_width=True)

            # 2nd Leg Table
            st.subheader("2nd Leg Table")
            df_leg_2 = filter_leg_matches(df, selected_season, leg='2nd', matchday=selected_matchday)
            if df_leg_2.empty:
                st.write("No available data yet.")
            else:
                df_leg_2_points = calculate_leg_points(df_leg_2)
                leg_2_fig = plot_leg_table(df_leg_2_points, f'2nd Leg Table After Matchday {selected_matchday} ({selected_season})', color_codes_df)
                st.plotly_chart(leg_2_fig, use_container_width=True)

        elif st.session_state.selected_view == "Cross Table":
            display_cross_table_view(df, selected_season, selected_matchday)

        # Season Data Section
        st.header("Season Data")

        # Define the initial state for the selected visualization
        if "selected_viz" not in st.session_state:
            st.session_state.selected_viz = "Bump Chart"

        # Create buttons and update the selected visualization
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Bump Chart", key="bump_chart_button"):
                st.session_state.selected_viz = "Bump Chart"
        with col2:
            if st.button("Pie Chart", key="pie_chart_button"):
                st.session_state.selected_viz = "Pie Chart"
        with col3:
            if st.button("Heat Map", key="heat_map_button"):
                st.session_state.selected_viz = "Heat Map"
        with col4:
            if st.button("Histogram", key="histogram_button"):
                st.session_state.selected_viz = "Histogram"

        # Display the selected visualization
        if st.session_state.selected_viz == "Bump Chart":
            display_bump_chart(df, selected_season, selected_matchday, color_codes_df)
        elif st.session_state.selected_viz == "Pie Chart":
            display_pie_chart(df, selected_season, selected_matchday)
        elif st.session_state.selected_viz == "Heat Map":
            display_heat_map(df, selected_season, selected_matchday)
        elif st.session_state.selected_viz == "Histogram":
            display_histogram(df, selected_season, selected_matchday)

    else:
        st.write("Please select a season, matchday, and fixture.")
