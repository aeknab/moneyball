import pandas as pd
import streamlit as st
from bundesliga.utils import resize_image, load_image
from bundesliga.table_display import display_styled_team_table
from bundesliga.team_data import get_team_data, get_movement
from bundesliga.season_selection import select_season_match_fixture

def display_match_preview(df):
    st.header("Matchday Analysis")

    # Use the centralized function for season, matchday, and fixture selection
    selected_season, selected_matchday, selected_match, df_matches = select_season_match_fixture(df)

    # Ensure that the selection is valid before proceeding
    if selected_season == '--' or selected_matchday == '--' or selected_match == '--':
        # Don't show warnings before any selection is made
        return selected_season, selected_matchday, selected_match, None, None, None

    # Filter the DataFrame for the selected season
    df_season = df[df['Season'] == selected_season]

    # Ensure we have valid matches for the selected season and matchday
    if df_season.empty:
        st.warning("No matches available for the selected season or matchday.")
        return selected_season, selected_matchday, selected_match, None, None, None

    # Fetch the selected match row
    selected_match_row = df_season[df_season.apply(lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1) == selected_match].iloc[0]

    # Assign team tags and other match details
    home_team_tag = selected_match_row['Home Tag']
    away_team_tag = selected_match_row['Away Tag']
    home_team = selected_match_row['Home Team']
    away_team = selected_match_row['Away Team']
    matchday = selected_match_row['Matchday']
    match_date_str = selected_match_row['Match Date']
    match_time = selected_match_row['Match Time']
    stadium = selected_match_row['Stadium']
    location = selected_match_row['Location']

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
        st.markdown(
            f"<div style='text-align: center; font-size: 24px;'><b>{home_team}</b></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='text-align: center; font-size: 20px;'>vs.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='text-align: center; font-size: 24px;'><b>{away_team}</b></div>",
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
        st.image(away_logo_resized, use_column_width=False)

    # Display match outcome or input fields
    row2_col1, row2_col2, row2_col3 = st.columns([1, 2, 1])

    with row2_col1:
        # Load the stadium image (optional)
        stadium_image_path = f"data/logos/stadiums/{home_team_tag}_stadium.png"
        stadium_image = load_image(stadium_image_path)
        stadium_image_resized = resize_image(stadium_image, 10000)
        st.image(stadium_image_resized, use_column_width=False)

    with row2_col2:
        # Display or input match outcome
        if selected_season == '2023/24':
            # Input for current season
            col2_left, col2_mid, col2_right = st.columns([1, 0.2, 1])

            with col2_left:
                home_goals = col2_left.number_input("", min_value=0, max_value=20, value=0, step=1, key="home_goals")

            with col2_mid:
                st.markdown("<div style='font-size: 30px; line-height: 3;'>:</div>", unsafe_allow_html=True)

            with col2_right:
                away_goals = col2_right.number_input("", min_value=0, max_value=20, value=0, step=1, key="away_goals")

        else:
            # Display the outcome for older seasons
            match_outcome = f"{selected_match_row['Home Goals']} : {selected_match_row['Away Goals']}"
            st.markdown(
                f"<div style='text-align: center; font-size: 60px; font-family: Courier; color: #FFFF4F; margin-top: -10px;'>"
                f"{match_outcome}</div>",
                unsafe_allow_html=True
)

    with row2_col3:
        # Bundesliga logo (optional)
        bundesliga_logo_path = "data/logos/team_logos/Bundesliga.svg.png"
        bundesliga_logo = load_image(bundesliga_logo_path)
        bundesliga_logo_resized = resize_image(bundesliga_logo, 6000)
        st.image(bundesliga_logo_resized, use_column_width=False)

    # Display the Teams Overview section using team data
    st.subheader("Teams Overview")
    is_current_season = selected_season == '2023/24'

    # Fetch team data using the filtered DataFrame `df_season` for the selected season
    home_data = get_team_data(df_season, home_team_tag, matchday, is_current_season)
    away_data = get_team_data(df_season, away_team_tag, matchday, is_current_season)

    # Swap teams to display the higher-ranked team on top
    if home_data['rank'] != '--' and away_data['rank'] != '--':
        if int(home_data['rank']) > int(away_data['rank']):
            home_data, away_data = away_data, home_data

    # Display the styled team table from `table_display.py`
    display_styled_team_table(home_data, away_data)

    return selected_season, selected_matchday, selected_match, df_matches, home_team_tag, away_team_tag