import streamlit as st
import pandas as pd
from modules.utils import resize_image, get_team_colors, load_image
from modules.match_preview_functions import get_last_5_matches, get_last_10_meetings, plot_last_10_meetings, generate_form_guide

def display_match_preview(df, colors):
    st.header("Bundesliga Match Preview")

    # Layout for filters: Place them side by side
    col1, col2, col3 = st.columns(3)  # Ensure columns are created correctly

    # Filter by Season
    with col1:
        seasons = ['--'] + sorted(df['Season'].unique(), reverse=True)
        selected_season = st.selectbox("Season", seasons)
    
    st.write("Selected Season:", selected_season)  # Debugging output

    if selected_season != '--':
        df_season = df[df['Season'] == selected_season]
        st.write(df_season.head())  # Display the first few rows of filtered data for the season
        st.write(df_season['Matchday'].unique())  # Display the unique matchdays available
    else:
        df_season = pd.DataFrame()

    # Filter by Matchday
    with col2:
        if not df_season.empty:
            matchdays = ['--'] + sorted(df_season['Matchday'].unique(), reverse=True)
            selected_matchday = st.selectbox("Matchday", matchdays)
        else:
            selected_matchday = '--'
    
    st.write("Selected Matchday:", selected_matchday)  # Debugging output

    # Filter by Fixture
    with col3:
        if selected_matchday != '--':
            df_matches = df_season[df_season['Matchday'] == selected_matchday]
            st.write(df_matches.head())  # Display the first few rows of filtered data for the matchday
            match_options = ['--'] + df_matches.apply(
                lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1).tolist()
            selected_match = st.selectbox("Fixture", match_options)
        else:
            selected_match = '--'
    
    st.write("Selected Fixture:", selected_match)  # Debugging output

    # Now, only proceed if all selections are valid
    if selected_season != '--' and selected_matchday != '--' and selected_match != '--':
        df_matches_sorted = df_matches.sort_values(by=['Match Date', 'Match Time'])

        if not df_matches_sorted.empty:
            selected_match_row = df_matches_sorted[
                df_matches_sorted.apply(lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1) == selected_match
            ].iloc[0]

            # Assign values to variables only after checking the validity
            matchday = selected_match_row['Matchday']
            home_team = selected_match_row['Home Team']
            away_team = selected_match_row['Away Team']
            home_team_tag = selected_match_row['Home Tag']
            away_team_tag = selected_match_row['Away Tag']
            match_date_str = selected_match_row['Match Date']
            match_time = selected_match_row['Match Time']
            stadium = selected_match_row['Stadium']
            location = selected_match_row['Location']

            # Load and resize the logos
            home_logo_path = f"data/logos/{home_team_tag}.svg.png"
            away_logo_path = f"data/logos/{away_team_tag}.svg.png"

            home_logo = load_image(home_logo_path)
            away_logo = load_image(away_logo_path)

            # Define maximum width and height for logos
            max_width = 100  # Maximum width in pixels
            max_height = 100  # Maximum height in pixels

            home_logo_resized = resize_image(home_logo, max_width, max_height)
            away_logo_resized = resize_image(away_logo, max_width, max_height)

            col1, col2, col3 = st.columns([1, 3, 1])

            with col1:
                st.image(home_logo_resized, use_column_width=False)

            with col2:
                st.markdown(f"<div style='text-align: center; font-size: 24px;'><b>{home_team}</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 20px;'>vs.</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 24px;'><b>{away_team}</b></div>", unsafe_allow_html=True)

            with col3:
                st.image(away_logo_resized, use_column_width=False)

            # Convert the date string to a datetime object
            match_date = pd.to_datetime(match_date_str)

            # Convert the time string to a datetime object and format it
            match_time = pd.to_datetime(match_time).strftime('%H:%M')  # Formats as HH:MM

            # Now you can format the date
            match_date_formatted = match_date.strftime('%A, %d. %B, %Y')

            # Display the first section
            st.markdown(f"<div style='text-align: center;'>{match_date_formatted} @ {match_time}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center;'>{stadium}, {location}</div>", unsafe_allow_html=True)

            # Get team data for both teams (only after confirming match details are valid)
            home_data = get_team_data(home_team_tag, matchday)
            away_data = get_team_data(away_team_tag, matchday)

    # Get team data for both teams
    def get_team_data(team_tag, matchday):
        previous_matchday = matchday - 1
        if previous_matchday <= 0:
            return {
                'rank': '--',
                'points': '--',
                'goals_scored': '--',
                'goals_conceded': '--',
                'gd': '--',
                'previous_rank': '--'
            }

        # Retrieve the previous matchday's data
        previous_match_row_home = df_season[(df_season['Matchday'] == previous_matchday) & (df_season['Home Tag'] == team_tag)]
        previous_match_row_away = df_season[(df_season['Matchday'] == previous_matchday) & (df_season['Away Tag'] == team_tag)]

        # Retrieve data from two matchdays ago (for movement comparison)
        two_matchdays_ago = matchday - 2
        two_matchdays_ago_row_home = df_season[(df_season['Matchday'] == two_matchdays_ago) & (df_season['Home Tag'] == team_tag)]
        two_matchdays_ago_row_away = df_season[(df_season['Matchday'] == two_matchdays_ago) & (df_season['Away Tag'] == team_tag)]

        # Get rank and other stats from either home or away columns for the previous matchday
        if not previous_match_row_home.empty:
            previous_rank = previous_match_row_home.iloc[0]['Home Team Rank']
        elif not previous_match_row_away.empty:
            previous_rank = previous_match_row_away.iloc[0]['Away Team Rank']
        else:
            previous_rank = '--'  # Handle case where there's no data for the previous matchday

        # Get rank from two matchdays ago to compare with the previous matchday
        if not two_matchdays_ago_row_home.empty:
            rank_two_matchdays_ago = two_matchdays_ago_row_home.iloc[0]['Home Team Rank']
        elif not two_matchdays_ago_row_away.empty:
            rank_two_matchdays_ago = two_matchdays_ago_row_away.iloc[0]['Away Team Rank']
        else:
            rank_two_matchdays_ago = previous_rank  # If no data for two matchdays ago, use previous matchday rank

        # Determine the team's current position
        if not previous_match_row_home.empty:
            row = previous_match_row_home.iloc[0]
            rank = row['Home Team Rank']
            points = row['Home Team Points']
            goals_scored = row['Home Team Goals Scored']
            goals_conceded = row['Home Team Goals Conceded']
            gd = row['Home Team GD']
        else:
            row = previous_match_row_away.iloc[0]
            rank = row['Away Team Rank']
            points = row['Away Team Points']
            goals_scored = row['Away Team Goals Scored']
            goals_conceded = row['Away Team Goals Conceded']
            gd = row['Away Team GD']

        return {
            'rank': rank,
            'points': points,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'gd': gd,
            'previous_rank': rank_two_matchdays_ago  # Use rank from two matchdays ago
        }

    # Get team data for both teams
    home_data = get_team_data(home_team_tag, matchday)
    away_data = get_team_data(away_team_tag, matchday)

    # Determine movement (up, down, or same)
    def get_movement(rank, previous_rank):
        if previous_rank == '--' or rank == '--':
            return '--'
        elif int(rank) < int(previous_rank):
            return '⬆️'  # Moved up
        elif int(rank) > int(previous_rank):
            return '⬇️'  # Moved down
        else:
            return '⏺️'  # Stayed the same

    home_data['movement'] = get_movement(home_data['rank'], home_data['previous_rank'])
    away_data['movement'] = get_movement(away_data['rank'], away_data['previous_rank'])

    # Function to display the header row
    def display_header():
        # Ensure the number of columns matches the number of elements in the list
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([1.1, 1, 5, 1.5, 0.75, 0.75, 0.75, 1.75, 1, 1.5])
        
        with col1:
            st.write("**Rank**")
        
        with col2:
            st.write("↕")
        
        with col3:
            st.write("**Team**")
        
        with col4:
            st.write("**Games**")
        
        with col5:
            st.write("**W**")
        
        with col6:
            st.write("**T**")
        
        with col7:
            st.write("**L**")
        
        with col8:
            st.write("**Goals**")
        
        with col9:
            st.write("**GD**")
        
        with col10:
            st.write("**Points**")
    
    # Function to calculate team statistics (games, wins, ties, losses)
    def calculate_team_stats(df_season, team):
        df_filtered = df_season[df_season['Matchday'] < matchday]
        games = len(df_filtered[(df_filtered['Home Team'] == team) | (df_filtered['Away Team'] == team)])
        wins = len(df_filtered[((df_filtered['Home Team'] == team) & (df_filtered['Home Goals'] > df_filtered['Away Goals'])) |
                               ((df_filtered['Away Team'] == team) & (df_filtered['Away Goals'] > df_filtered['Home Goals']))])
        ties = len(df_filtered[((df_filtered['Home Team'] == team) | (df_filtered['Away Team'] == team)) & 
                               (df_filtered['Home Goals'] == df_filtered['Away Goals'])])
        losses = games - (wins + ties)

        return games, wins, ties, losses
    
    # Function to display the team data
    def display_team_data(df_season, team_data, team_name, team_tag):
        games, wins, ties, losses = calculate_team_stats(df_season, team_name)
        
        # Load and resize the team logo
        team_logo_path = f"data/logos/{team_tag}.svg.png"
        team_logo = load_image(team_logo_path)
    
        # Define maximum width and height for logos
        max_width = 25  # Adjust as needed for Teams Overview
        max_height = 25  # Adjust as needed for Teams Overview
    
        team_logo_resized = resize_image(team_logo, max_width, max_height)
    
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([1.1, 1, 5, 1.5, 0.75, 0.75, 0.75, 1.75, 1, 1.5])
        
        with col1:
            st.write(f"{team_data['rank']}")
        
        with col2:
            st.write(f"{team_data['movement']}")
        
        with col3:
            # Create a horizontal layout for logo and team name
            col3a, col3b = st.columns([1, 4])
            
            with col3a:
                st.image(team_logo_resized, use_column_width=False)
            
            with col3b:
                st.write(f"{team_name}")
        
        with col4:
            st.write(f"{games}")
        
        with col5:
            st.write(f"{wins}")
        
        with col6:
            st.write(f"{ties}")
        
        with col7:
            st.write(f"{losses}")
        
        with col8:
            st.write(f"{team_data['goals_scored']} : {team_data['goals_conceded']}")
        
        with col9:
            st.write(f"{team_data['gd']}")
        
        with col10:
            st.write(f"**{team_data['points']}**")

    # Second Section - Display Teams Data
    st.subheader("Teams Overview")

    # Display the header
    display_header()

    # Determine the top and bottom teams
    if home_data['rank'] != '--' and away_data['rank'] != '--':
        if int(home_data['rank']) < int(away_data['rank']):
            top_team_data = home_data
            top_team_name = home_team
            top_team_tag = home_team_tag
            bottom_team_data = away_data
            bottom_team_name = away_team
            bottom_team_tag = away_team_tag
        else:
            top_team_data = away_data
            top_team_name = away_team
            top_team_tag = away_team_tag
            bottom_team_data = home_data
            bottom_team_name = home_team
            bottom_team_tag = home_team_tag
    else:
        top_team_data = home_data
        top_team_name = home_team
        top_team_tag = home_team_tag
        bottom_team_data = away_data
        bottom_team_name = away_team
        bottom_team_tag = away_team_tag

    # Display the teams sorted by rank
    display_team_data(df_season, top_team_data, top_team_name, top_team_tag)
    display_team_data(df_season, bottom_team_data, bottom_team_name, bottom_team_tag)
    
    # Third Section - Last 5 Matches
    col1, col2 = st.columns(2)
    
    # Get last 5 matches for both teams
    home_team_matches = get_last_5_matches(df_season, home_team, matchday)
    away_team_matches = get_last_5_matches(df_season, away_team, matchday)
    
    # Update the header for the home team
    if home_team_matches[3] > 0:
        col1.subheader(f"Last {home_team_matches[3]} Match{'es' if home_team_matches[3] > 1 else ''} for {home_team_tag}")
        for i in range(len(home_team_matches[0])):
            col1.write(f"{home_team_matches[0][i]} | **{home_team_matches[1][i]}** | {home_team_matches[2][i]}")
    else:
        col1.subheader(f"No matches for {home_team_tag} yet")
    
    # Update the header for the away team
    if away_team_matches[3] > 0:
        col2.subheader(f"Last {away_team_matches[3]} Match{'es' if away_team_matches[3] > 1 else ''} for {away_team_tag}")
        for i in range(len(away_team_matches[0])):
            col2.write(f"{away_team_matches[0][i]} | **{away_team_matches[1][i]}** | {away_team_matches[2][i]}")
    else:
        col2.subheader(f"No matches for {away_team_tag} yet")

    # Fourth Section - Last 10 Meetings        
    # Get the last 10 meetings data
    current_season = selected_season  # Assuming `selected_season` is already set to the current season in the app
    plot_last_10_meetings(df, home_team_tag, away_team_tag, colors, matchday, current_season)

    # Fifth Section - Team Form Guide
    st.subheader("Team Form Guide")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**{home_team} Form Guide**")
        generate_form_guide(home_team, matchday, df_season)

    with col2:
        st.write(f"**{away_team} Form Guide**")
        generate_form_guide(away_team, matchday, df_season)

