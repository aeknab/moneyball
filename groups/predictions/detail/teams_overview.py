import streamlit as st
import pandas as pd
from PIL import Image
from ..utils import resize_image, load_image

# Function to display match preview with details for both teams
def display_match_preview(match_row=None, df=None, predictions_mode=False):

    # Ensure that df is not None
    if df is None:
        st.error("Data for matches (df) is missing.")
        return

    if predictions_mode and match_row is not None:
        selected_season = '2023/24'
        selected_matchday = match_row['Matchday']
        df_matches = df[df['Matchday'] == selected_matchday]
    else:
        selected_season, selected_matchday, df_matches, match_row = handle_non_predictions_mode(df)
        if not selected_season or not selected_matchday or not match_row:
            return

    # Extract match details
    home_team_tag, away_team_tag, home_team, away_team = extract_match_details(match_row)

    # Display team logos and match info
    display_team_logos(home_team_tag, away_team_tag, home_team, away_team, match_row)

    # Display outcome or prediction inputs
    display_match_outcome_or_predictions(predictions_mode, match_row, selected_season)

    # Display Teams Overview
    display_teams_overview(df, home_team_tag, away_team_tag, selected_season)

    return selected_season, selected_matchday, match_row, df_matches, home_team_tag, away_team_tag

# Function to handle non-predictions mode (interactive UI for season, matchday, and fixture selection)
def handle_non_predictions_mode(df):
    col1, col2, col3 = st.columns(3)

    with col1:
        seasons = ['--'] + sorted(df['Season'].unique(), reverse=True)
        selected_season = st.selectbox("Season", seasons)

    if selected_season == '--':
        return None, None, None, None

    with col2:
        df_season = df[df['Season'] == selected_season]
        matchdays = ['--'] + sorted(df_season['Matchday'].unique(), reverse=True)
        selected_matchday = st.selectbox("Matchday", matchdays)

    if selected_matchday == '--':
        return selected_season, None, None, None

    with col3:
        df_matches = df_season[df_season['Matchday'] == selected_matchday]
        match_options = ['--'] + df_matches.apply(lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1).tolist()
        selected_match = st.selectbox("Fixture", match_options)

    if selected_match == '--':
        return selected_season, selected_matchday, None, None

    selected_match_row = df_matches[
        df_matches.apply(lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1) == selected_match
    ].iloc[0]

    return selected_season, selected_matchday, df_matches, selected_match_row

# Function to extract details from the match row
def extract_match_details(match_row):
    home_team_tag = match_row['Home Tag']
    away_team_tag = match_row['Away Tag']
    home_team = match_row['Home Team']
    away_team = match_row['Away Team']
    return home_team_tag, away_team_tag, home_team, away_team

# Function to display team logos and match information
def display_team_logos(home_team_tag, away_team_tag, home_team, away_team, match_row):
    home_logo_path = f"data/logos/team_logos/{home_team_tag}.svg.png"
    away_logo_path = f"data/logos/team_logos/{away_team_tag}.svg.png"

    home_logo = load_image(home_logo_path)
    away_logo = load_image(away_logo_path)

    target_area = 10000
    home_logo_resized = resize_image(home_logo, target_area)
    away_logo_resized = resize_image(away_logo, target_area)

    row1_col1, row1_col2, row1_col3 = st.columns([1, 3, 1])
    # Add custom CSS for spacing, inside row1_col2
    st.markdown("""
        <style>
        .team-info { margin-bottom: 20px; } /* Adjust the margin as needed */
        </style>
        """, unsafe_allow_html=True)

    with row1_col1:
        st.image(home_logo_resized, use_column_width=False)

    with row1_col2:
        # Updated to display team names and "vs." on separate lines
        st.markdown(
            f"<div style='text-align: center; font-size: 24px; line-height: 1.2;'>"
            f"<b>{home_team}</b><br>"
            f"<span style='font-size: 20px;'>vs.</span><br>"
            f"<b>{away_team}</b></div>", 
            unsafe_allow_html=True)
        display_match_info(match_row)

    with row1_col3:
        st.image(away_logo_resized, use_column_width=False)

# Function to display match information like date, time, and location
def display_match_info(match_row):
    match_date_str = match_row['Match Date']
    match_time = match_row['Match Time']
    stadium = match_row['Stadium']
    location = match_row['Location']

    match_date = pd.to_datetime(match_date_str)
    match_time_formatted = pd.to_datetime(match_time).strftime('%H:%M')
    day = match_date.strftime('%d').lstrip('0')
    month_year = match_date.strftime('%B, %Y')
    weekday = match_date.strftime('%A')
    match_date_formatted = f"{weekday}, {day}. {month_year} @ {match_time_formatted}"

    st.markdown(
        f"<div style='text-align: center; font-size: 14px; color: grey;'>{match_date_formatted}</div>", 
        unsafe_allow_html=True)
    st.markdown(
        f"<div style='text-align: center; font-size: 14px; color: grey;'>{stadium}, {location}</div>", 
        unsafe_allow_html=True)

# Function to display match outcome or input for predictions
def display_match_outcome_or_predictions(predictions_mode, match_row, selected_season):
    stadium_image_path = f"data/logos/stadiums/{match_row['Home Tag']}_stadium.png"
    bundesliga_logo_path = "data/logos/team_logos/Bundesliga.svg.png"

    stadium_image = load_image(stadium_image_path)
    bundesliga_logo = load_image(bundesliga_logo_path)

    stadium_image_resized = resize_image(stadium_image, 10000)
    bundesliga_logo_resized = resize_image(bundesliga_logo, 6000)

    row2_col1, row2_col2, row2_col3 = st.columns([1, 2, 1])

    with row2_col1:
        st.image(stadium_image_resized, use_column_width=False)

    with row2_col2:
        if selected_season == '2023/24' and predictions_mode:
            st.markdown("""
                <style>
                div[data-baseweb="input"] {
                    margin-top: 0px !important;
                }
                </style>
            """, unsafe_allow_html=True)

            col2_left, col2_mid, col2_right = st.columns([1, 0.2, 1])
            with col2_left:
                home_goals = st.number_input("", min_value=0, max_value=11, value=0, step=1, key="home_goals", format="%d")
            with col2_mid:
                # Center the colon using CSS
                st.markdown("""
                    <style>
                    .centered-colon {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 100%;
                        font-size: 30px;
                    }
                    </style>
                    <div class="centered-colon">:</div>
                """, unsafe_allow_html=True)
            with col2_right:
                away_goals = st.number_input("", min_value=0, max_value=11, value=0, step=1, key="away_goals", format="%d")
        else:
            match_outcome = f"{match_row['Home Goals']} : {match_row['Away Goals']}"
            st.markdown(
                f"<div style='text-align: center; font-size: 60px; font-family: Courier; color: #FFFF4F;'>{match_outcome}</div>", 
                unsafe_allow_html=True)

    with row2_col3:
        st.image(bundesliga_logo_resized, use_column_width=False)

# Function to display Teams Overview
def display_teams_overview(df, home_team_tag, away_team_tag, selected_season):
    st.subheader("Teams Overview")

    # Filter the DataFrame for the selected season
    season_df = df[df['Season'] == selected_season]

    # Get data for the home and away teams
    try:
        home_team_data = season_df[season_df['Home Tag'] == home_team_tag].iloc[0]
        away_team_data = season_df[season_df['Home Tag'] == away_team_tag].iloc[0]
    except IndexError:
        st.error(f"No data found for {home_team_tag} or {away_team_tag} in the selected season.")
        return

    # Define the available columns and provide default values if they don't exist
    overview_data = {
        'Rank': [home_team_data.get('Rank', '--'), away_team_data.get('Rank', '--')],
        'Games': [home_team_data.get('Games', '--'), away_team_data.get('Games', '--')],
        'W': [home_team_data.get('W', '--'), away_team_data.get('W', '--')],
        'T': [home_team_data.get('T', '--'), away_team_data.get('T', '--')],
        'L': [home_team_data.get('L', '--'), away_team_data.get('L', '--')],
        'Goals': [f"{home_team_data.get('Home Goals', '--')} : {home_team_data.get('Away Goals', '--')}",
                  f"{away_team_data.get('Home Goals', '--')} : {away_team_data.get('Away Goals', '--')}"],
        'GD': [home_team_data.get('GD', '--'), away_team_data.get('GD', '--')],
        'Points': [home_team_data.get('Points', '--'), away_team_data.get('Points', '--')]
    }

    # Create a DataFrame for displaying the overview table
    teams_overview = pd.DataFrame({
        'Team': [home_team_data['Home Team'], away_team_data['Home Team']],
        'Rank': overview_data['Rank'],
        'Games': overview_data['Games'],
        'W': overview_data['W'],
        'T': overview_data['T'],
        'L': overview_data['L'],
        'Goals': overview_data['Goals'],
        'GD': overview_data['GD'],
        'Points': overview_data['Points']
    })

    # Display the overview table
    st.table(teams_overview)