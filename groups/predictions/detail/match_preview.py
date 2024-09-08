import streamlit as st
import pandas as pd
from predictions.detail.bundesliga.utils import resize_image, load_image
from shared.team_data import get_team_data, get_movement
from shared.display_utils import display_styled_team_table

def display_match_preview(match_row=None, predictions_mode=False):
    if match_row is None:
        st.error("No match information provided.")
        return

    if predictions_mode:
        # Directly use the passed match_row and the season is fixed to 2023/24 in predictions mode
        selected_season = '2023/24'
        selected_matchday = match_row['Matchday']  # Extract matchday from match_row
        home_team_tag = match_row['Home Tag']
        away_team_tag = match_row['Away Tag']
        home_team = match_row['Home Team']
        away_team = match_row['Away Team']
        match_date_str = match_row['Match Date']
        match_time = match_row['Match Time']
        stadium = match_row['Stadium']
        location = match_row['Location']

        # Display team data using the shared get_team_data function
        home_data = get_team_data(home_team_tag, selected_matchday, True, predictions_mode, match_row)
        away_data = get_team_data(away_team_tag, selected_matchday, True, predictions_mode, match_row)

        # Load and resize the logos
        home_logo_path = f"data/logos/team_logos/{home_team_tag}.svg.png"
        away_logo_path = f"data/logos/team_logos/{away_team_tag}.svg.png"

        home_logo = load_image(home_logo_path)
        away_logo = load_image(away_logo_path)

        home_logo_resized = resize_image(home_logo, 10000)
        away_logo_resized = resize_image(away_logo, 10000)

        # Display the first row: team logos, match info, and matchday details
        row1_col1, row1_col2, row1_col3 = st.columns([1, 3, 1])

        with row1_col1:
            st.image(home_logo_resized, use_column_width=False)

        with row1_col2:
            st.markdown(f"<div style='text-align: center; font-size: 24px;'><b>{home_team}</b> vs. <b>{away_team}</b></div>", unsafe_allow_html=True)
            match_date = pd.to_datetime(match_date_str)
            match_time_formatted = pd.to_datetime(match_time).strftime('%H:%M')
            match_date_formatted = f"{match_date.strftime('%A')}, {match_date.strftime('%d').lstrip('0')}. {match_date.strftime('%B, %Y')} @ {match_time_formatted}"
            st.markdown(f"<div style='text-align: center; font-size: 14px; color: grey;'>{match_date_formatted}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center; font-size: 14px; color: grey;'>{stadium}, {location}</div>", unsafe_allow_html=True)

        with row1_col3:
            st.image(away_logo_resized, use_column_width=False)

        # Display team data in a styled table
        home_data['movement'] = get_movement(home_data['rank'], home_data.get('previous_rank', '--'))
        away_data['movement'] = get_movement(away_data['rank'], away_data.get('previous_rank', '--'))

        if home_data['rank'] != '--' and away_data['rank'] != '--' and int(home_data['rank']) > int(away_data['rank']):
            home_data, away_data = away_data, home_data  # Ensure better-ranked team is on top

        display_styled_team_table(home_data, away_data, home_team, away_team)

        # Additional match details like logos, stadium image, and more
        stadium_image_path = f"data/logos/stadiums/{home_team_tag}_stadium.png"
        bundesliga_logo_path = "data/logos/team_logos/Bundesliga.svg.png"

        stadium_image = load_image(stadium_image_path)
        bundesliga_logo = load_image(bundesliga_logo_path)

        stadium_image_resized = resize_image(stadium_image, 10000)
        bundesliga_logo_resized = resize_image(bundesliga_logo, 6000)

        # Display the match outcome or input fields and add the images to the sides
        row2_col1, row2_col2, row2_col3 = st.columns([1, 2, 1])

        with row2_col1:
            st.image(stadium_image_resized, use_column_width=False)

        with row2_col2:
            # Here you can add score input for predictions mode
            if predictions_mode:
                st.markdown("""
                    <style>
                    div[data-baseweb="input"] {
                        margin-top: 0px !important;  /* Force the input fields to move up */
                    }
                    </style>
                """, unsafe_allow_html=True)
                col2_left, col2_mid, col2_right = st.columns([1, 0.2, 1])
                with col2_left:
                    home_goals = col2_left.number_input("", min_value=0, max_value=11, value=0, step=1, key="home_goals", format="%d")
                with col2_mid:
                    st.markdown(
                        "<div style='font-size: 30px; line-height: 3; padding-bottom: 30px; display: flex; align-items: flex-end; height: 100%; justify-content: center;'>:</div>",
                        unsafe_allow_html=True
                    )
                with col2_right:
                    away_goals = col2_right.number_input("", min_value=0, max_value=11, value=0, step=1, key="away_goals", format="%d")
            else:
                st.error("Prediction input is only available in prediction mode.")

        with row2_col3:
            st.image(bundesliga_logo_resized, use_column_width=False)

    else:
        st.error("This function should only be used in predictions mode.")