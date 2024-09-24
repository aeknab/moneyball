import streamlit as st
import pandas as pd
from bundesliga.data_loader import load_data
from bundesliga.match_preview import display_match_preview
from bundesliga.form_guide_last_5 import display_form_guide_section
from bundesliga.form_guide_last_10 import plot_last_10_meetings
from bundesliga.form_guide_season import display_donut_charts_side_by_side
from bundesliga.league_table import display_league_tables
from bundesliga.bump_chart import display_bump_chart
from bundesliga.pie_chart import display_pie_chart
from bundesliga.heat_map import display_heat_map
from bundesliga.histogram import display_histogram
from bundesliga.first_and_second import filter_leg_matches, calculate_leg_points, plot_leg_table
from bundesliga.crosstable import display_cross_table_view
from bundesliga.home_away import filter_home_away_matches, calculate_home_away_points, plot_home_away_table

def display_bundesliga_page():
    # Load data once, to be used across the app
    df = load_data()

    # Load color codes
    color_codes_df = pd.read_csv("data/color_codes.csv")

    # Streamlit app layout
    st.title("Bundesliga Dashboard")

    # Bundesliga Section
    selected_season, selected_matchday, selected_match, df_matches, home_team_tag, away_team_tag = display_match_preview(df)

    # Ensure selections are made before proceeding
    if selected_season != '--' and selected_matchday != '--' and selected_match != '--':
        selected_match_row = df_matches[
            df_matches.apply(lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1) == selected_match
        ].iloc[0]

        home_team_tag = selected_match_row['Home Tag']
        away_team_tag = selected_match_row['Away Tag']

        selected_teams = [home_team_tag, away_team_tag]  # Define the selected teams

        # Display the form guide sections
        display_form_guide_section(df, selected_season, selected_matchday, selected_match, df_matches)

        # Display the season form guide donut charts
        display_donut_charts_side_by_side(
            selected_match_row['Home Team'],
            selected_match_row['Away Team'],
            home_team_tag,
            away_team_tag,
            selected_matchday,
            df[df['Season'] == selected_season]
        )

        # Display the last 10 meetings
        plot_last_10_meetings(df, home_team_tag, away_team_tag, color_codes_df, selected_matchday, selected_season)

        # League Table Section with Radio Buttons
        st.header("League Table")

        # Use radio buttons for better state management
        table_options = ["Season Table", "Home/Away Table", "1st/2nd Leg Table", "Cross Table"]
        selected_view = st.radio("Select Table View:", table_options, index=0, horizontal=True)

        # Display the selected table
        if selected_view == "Season Table":
            display_league_tables(df, selected_season, selected_matchday, "Season Table", color_codes_df, selected_teams)

        elif selected_view == "Home/Away Table":
            # Display Home and Away tables one after the other
            st.subheader("Home Table")
            df_filtered = filter_home_away_matches(df, selected_season, selected_matchday)
            df_home_points = calculate_home_away_points(df_filtered, home_away='home')
            home_fig = plot_home_away_table(
                df_home_points,
                f'Home Table After Matchday {selected_matchday} ({selected_season})',
                color_codes_df,
                home_away='home'
            )
            st.plotly_chart(home_fig, use_container_width=True)

            st.subheader("Away Table")
            df_away_points = calculate_home_away_points(df_filtered, home_away='away')
            away_fig = plot_home_away_table(
                df_away_points,
                f'Away Table After Matchday {selected_matchday} ({selected_season})',
                color_codes_df,
                home_away='away'
            )
            st.plotly_chart(away_fig, use_container_width=True)

        elif selected_view == "1st/2nd Leg Table":
            # 1st Leg Table
            st.subheader("1st Leg Table")
            df_leg_1 = filter_leg_matches(df, selected_season, leg='1st', matchday=selected_matchday)
            if df_leg_1.empty:
                st.write("No available data yet.")
            else:
                df_leg_1_points = calculate_leg_points(df_leg_1)
                leg_1_fig = plot_leg_table(
                    df_leg_1_points,
                    f'1st Leg Table After Matchday {selected_matchday} ({selected_season})',
                    color_codes_df
                )
                st.plotly_chart(leg_1_fig, use_container_width=True)

            # 2nd Leg Table
            st.subheader("2nd Leg Table")
            df_leg_2 = filter_leg_matches(df, selected_season, leg='2nd', matchday=selected_matchday)
            if df_leg_2.empty:
                st.write("No available data yet.")
            else:
                df_leg_2_points = calculate_leg_points(df_leg_2)
                leg_2_fig = plot_leg_table(
                    df_leg_2_points,
                    f'2nd Leg Table After Matchday {selected_matchday} ({selected_season})',
                    color_codes_df
                )
                st.plotly_chart(leg_2_fig, use_container_width=True)

        elif selected_view == "Cross Table":
            display_cross_table_view(df, selected_season, selected_matchday)

        # Season Data Section
        st.header("Season Data")

        # Use radio buttons for visualization selection
        viz_options = ["Bump Chart", "Pie Chart", "Heat Map", "Histogram"]
        selected_viz = st.radio("Select Visualization:", viz_options, index=0, horizontal=True)

        # Display the selected visualization
        if selected_viz == "Bump Chart":
            display_bump_chart(df, selected_season, selected_matchday, color_codes_df, selected_teams)
        elif selected_viz == "Pie Chart":
            display_pie_chart(df, selected_season, selected_matchday)
        elif selected_viz == "Heat Map":
            display_heat_map(df, selected_season, selected_matchday)
        elif selected_viz == "Histogram":
            display_histogram(df, selected_season, selected_matchday)

#    else:
#        st.warning("Please select a season, matchday, and fixture.")