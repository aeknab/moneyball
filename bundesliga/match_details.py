import streamlit as st
import pandas as pd
from bundesliga.utils import resize_image, load_image

def display_match_details(df, selected_season, selected_match, home_team_tag, away_team_tag, matchday):
    # Fetch the selected match row
    selected_match_row = df[
        df.apply(lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1) == selected_match
    ].iloc[0]

    # Assign team tags and other match details
    home_team_tag = selected_match_row['Home Tag']
    away_team_tag = selected_match_row['Away Tag']
    home_team = selected_match_row['Home Team']
    away_team = selected_match_row['Away Team']
    match_date_str = selected_match_row['Match Date']
    match_time = selected_match_row['Match Time']
    stadium = selected_match_row['Stadium']
    location = selected_match_row['Location']

    # Load and resize the logos
    home_logo_path = f"data/logos/team_logos/{home_team_tag}.svg.png"
    away_logo_path = f"data/logos/team_logos/{away_team_tag}.svg.png"

    home_logo = load_image(home_logo_path)
    away_logo = load_image(away_logo_path)

    # Resize images based on target area for consistent size
    target_area = 10000  # Adjust this value to control the overall size
    home_logo_resized = resize_image(home_logo, target_area)
    away_logo_resized = resize_image(away_logo, target_area)

    # Display the first row: team logos, match info, and matchday details
    row1_col1, row1_col2, row1_col3 = st.columns([1, 3, 1])

    with row1_col1:
        st.markdown("<div style='display: flex; align-items: center; height: 100%; justify-content: center;'>", unsafe_allow_html=True)
        st.image(home_logo_resized, use_column_width=False)
        st.markdown("</div>", unsafe_allow_html=True)

    with row1_col2:
        st.markdown(
            f"<div style='text-align: center; font-size: 24px; margin-bottom: 0px;'><b>{home_team}</b></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='text-align: center; font-size: 20px; margin-bottom: 0px;'>vs.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='text-align: center; font-size: 24px; margin-bottom: 0px;'><b>{away_team}</b></div>",
            unsafe_allow_html=True
        )

        # Format the match date and time
        match_date = pd.to_datetime(match_date_str)
        match_time_formatted = pd.to_datetime(match_time).strftime('%H:%M')  # Formats as HH:MM
        day = match_date.strftime('%d').lstrip('0')
        month_year = match_date.strftime('%B, %Y')
        weekday = match_date.strftime('%A')
        match_date_formatted = f"{weekday}, {day}. {month_year} @ {match_time_formatted}"

        st.markdown(
            f"<div style='text-align: center; font-size: 14px; color: grey;'>{match_date_formatted}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='text-align: center; font-size: 14px; color: grey;'>{stadium}, {location}</div>",
            unsafe_allow_html=True
        )

    with row1_col3:
        st.markdown("<div style='display: flex; align-items: center; height: 100%; justify-content: center;'>", unsafe_allow_html=True)
        st.image(away_logo_resized, use_column_width=False)
        st.markdown("</div>", unsafe_allow_html=True)

    # Determine if the selected season is the current one (2023/24)
    is_current_season = selected_season == '2023/24'

    # Score input for the current season, and display of actual scores for past seasons
    st.markdown("### Match Outcome")
    if is_current_season:
        st.markdown("### Enter Match Outcome")
        col1, col2, col3 = st.columns([1, 0.2, 1])
        with col1:
            home_goals = st.number_input(f"{home_team} Goals", min_value=0, max_value=20, value=0, step=1, key='home_goals')
        with col2:
            st.markdown("<div style='font-size: 30px; line-height: 3; text-align: center;'>:</div>", unsafe_allow_html=True)
        with col3:
            away_goals = st.number_input(f"{away_team} Goals", min_value=0, max_value=20, value=0, step=1, key='away_goals')
    else:
        # Display the outcome for past seasons
        match_outcome = f"{selected_match_row['Home Goals']} : {selected_match_row['Away Goals']}"
        st.markdown(f"### Final Score: {match_outcome}")