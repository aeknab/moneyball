import streamlit as st
import pandas as pd
from groups.predictions.detail.teams_overview import display_match_preview
from groups.predictions.detail.bundesliga.form_guide_last_5 import display_form_guide_section
from groups.predictions.detail.bundesliga.form_guide_last_10 import plot_last_10_meetings
from groups.predictions.detail.bundesliga.form_guide_season import display_donut_charts_side_by_side
from groups.predictions.detail.bundesliga.league_table import display_league_tables
from groups.predictions.detail.bundesliga.bump_chart import display_bump_chart
from groups.predictions.detail.bundesliga.pie_chart import display_pie_chart
from groups.predictions.detail.bundesliga.heat_map import display_heat_map
from groups.predictions.detail.bundesliga.histogram import display_histogram

# Function to display the Detail View section of the predictions page
def display_predictions_detail():
    st.subheader("Matchday Predictions - Detail View")

    # Load the Bundesliga match preview data
    buli_df = pd.read_csv("data/buli_all_seasons.csv")

    # Load the color codes for charts
    try:
        color_codes_df = pd.read_csv("data/color_codes.csv")
    except FileNotFoundError:
        st.error("Color codes file not found. Please ensure 'data/color_codes.csv' exists.")
        return

    # Filter for the 2023/24 season
    buli_df_2023 = buli_df[buli_df['Season'] == '2023/24']

    # Dropdown to select matchday, defaulting to "--"
    matchdays = ['--'] + list(buli_df_2023['Matchday'].unique()[::-1])
    selected_matchday = st.selectbox("Select Matchday", options=matchdays, key="matchday_select_predictions_detail")

    # Ensure that a matchday is selected before proceeding
    if selected_matchday == '--':
        st.warning("Please select a matchday.")
        return

    # Filter matches for the selected matchday
    filtered_matches = buli_df_2023[buli_df_2023["Matchday"] == selected_matchday]

    # Check if there are any matches for the selected matchday
    if filtered_matches.empty:
        st.error(f"No matches found for Matchday {selected_matchday}.")
        return

    # Create a slider for selecting the match between the home and away teams
    match_slider = st.select_slider(
        "Select Match",
        options=[f"{row['Home Tag']} - {row['Away Tag']}" for _, row in filtered_matches.iterrows()],
        key="match_slider_predictions_detail"
    )

    # Find the match corresponding to the selected slider option
    selected_match_row = filtered_matches[
        filtered_matches.apply(lambda row: f"{row['Home Tag']} - {row['Away Tag']}", axis=1) == match_slider
    ]

    # Check if any match was selected and exists in the DataFrame
    if selected_match_row.empty:
        st.error(f"No match found for the selection {match_slider}.")
        return

    # Proceed to access the first match row (assuming one match was selected)
    selected_match_row = selected_match_row.iloc[0]

    # Pass the match row to other display functions
    display_match_preview(match_row=selected_match_row, df=buli_df_2023, predictions_mode=True)

    # Form Guide Section
    display_form_guide_section(buli_df_2023, '2023/24', selected_matchday, match_slider, filtered_matches)

    # Donut Charts
    display_donut_charts_side_by_side(selected_match_row['Home Team'], selected_match_row['Away Team'], 
                                      selected_match_row['Home Tag'], selected_match_row['Away Tag'], 
                                      selected_matchday, buli_df_2023)

    # Last 10 Meetings
    plot_last_10_meetings(buli_df_2023, selected_match_row['Home Tag'], selected_match_row['Away Tag'], 
                          color_codes_df, selected_matchday, '2023/24')

    # League Table Section
    st.header("League Table")
    display_league_tables(buli_df_2023, '2023/24', selected_matchday, "Season Table", color_codes_df, 
                          [selected_match_row['Home Tag'], selected_match_row['Away Tag']])

    # Additional visualizations (Bump Chart, Pie Chart, etc.)
    st.header("Season Data")
    display_bump_chart(buli_df_2023, '2023/24', selected_matchday, color_codes_df, 
                       [selected_match_row['Home Tag'], selected_match_row['Away Tag']])
    display_pie_chart(buli_df_2023, '2023/24', selected_matchday)
    display_heat_map(buli_df_2023, '2023/24', selected_matchday)
    display_histogram(buli_df_2023, '2023/24', selected_matchday)