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

    # Check if the matchday was selected in the Overview
    if 'selected_matchday' not in st.session_state:
        st.error("Please select a matchday in the Overview tab first.")
        return

    # Load the Bundesliga match preview data
    buli_df = pd.read_csv("data/buli_all_seasons.csv")

    # Filter for the 2023/24 season
    buli_df_2023 = buli_df[buli_df['Season'] == '2023/24']

    # Get the matchday from the session state (selected in Overview)
    selected_matchday = st.session_state.selected_matchday

    # Filter matches for the selected matchday
    filtered_matches = buli_df_2023[buli_df_2023["Matchday"] == selected_matchday]

    if filtered_matches.empty:
        st.error(f"No matches found for Matchday {selected_matchday}.")
        return

    # --- Display the matchday title at the top ---
    # st.subheader(f"Matchday {selected_matchday}")

    # Create buttons for each match and allow the user to select a match
    match_options = [f"{row['Home Tag']} - {row['Away Tag']}" for _, row in filtered_matches.iterrows()]

    # Check if a match was selected in the Overview
    if 'selected_match' in st.session_state:
        selected_match = st.session_state.selected_match
    else:
        # Default to the first match in the list if no match is selected yet
        selected_match = match_options[0]

    # Fix: Ensure selected match exists in match options for the selected matchday
    if selected_match not in match_options:
        selected_match = match_options[0]  # Reset to the first option

    selected_match = st.radio("", options=match_options, key="match_selection", index=match_options.index(selected_match))

    # Apply custom CSS to display the radio buttons in a horizontal line
    st.markdown("""
        <style>
        div[role="radiogroup"] {
            display: flex;
            flex-direction: row;  /* Align items horizontally */
        }
        </style>
        """, unsafe_allow_html=True)

    # Store selected match in session state
    st.session_state.selected_match = selected_match

    # Find the match corresponding to the selected button option
    selected_match_row = filtered_matches[
        filtered_matches.apply(lambda row: f"{row['Home Tag']} - {row['Away Tag']}", axis=1) == selected_match
    ]

    if selected_match_row.empty:
        st.error(f"No match found for the selection {selected_match}.")
        return

    selected_match_row = selected_match_row.iloc[0]

    # --- Pass the DataFrame and selected match row to the match preview function ---
    display_match_preview(match_row=selected_match_row, df=buli_df_2023, predictions_mode=True)

    # --- Load color codes for charts ---
    color_codes_df = pd.read_csv("data/color_codes.csv")

    # --- Display the form guide for both teams ---
    display_form_guide_section(buli_df_2023, '2023/24', selected_matchday, selected_match, filtered_matches)

    # --- Display donut charts for both teams ---
    display_donut_charts_side_by_side(
        selected_match_row['Home Team'], selected_match_row['Away Team'],
        selected_match_row['Home Tag'], selected_match_row['Away Tag'], 
        selected_matchday, buli_df_2023
    )

    # --- Display the last 10 meetings between the two teams ---
    plot_last_10_meetings(
        buli_df_2023, selected_match_row['Home Tag'], selected_match_row['Away Tag'],
        color_codes_df, selected_matchday, '2023/24'
    )

    # --- Display the League Table ---
    st.header("League Table")
    display_league_tables(
        buli_df_2023, '2023/24', selected_matchday, "Season Table", color_codes_df,
        [selected_match_row['Home Tag'], selected_match_row['Away Tag']]
    )

    # --- Additional Visualizations: Bump Chart, Pie Chart, Heat Map, etc. ---
    st.header("Season Data")
    display_bump_chart(buli_df_2023, '2023/24', selected_matchday, color_codes_df, 
                       [selected_match_row['Home Tag'], selected_match_row['Away Tag']])
    display_pie_chart(buli_df_2023, '2023/24', selected_matchday)
    display_heat_map(buli_df_2023, '2023/24', selected_matchday)
    display_histogram(buli_df_2023, '2023/24', selected_matchday)