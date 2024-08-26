import streamlit as st
import pandas as pd
from bundesliga.utils import resize_image, load_image

def display_match_preview(df):
    st.header("Bundesliga Match Preview")

    # Layout for filters: Place them side by side
    col1, col2, col3 = st.columns(3)

    # Dropdown for Season
    with col1:
        seasons = ['--'] + sorted(df['Season'].unique(), reverse=True)
        selected_season = st.selectbox("Season", seasons)

    # Dropdown for Matchday
    with col2:
        if selected_season != '--':
            df_season = df[df['Season'] == selected_season]
            matchdays = ['--'] + sorted(df_season['Matchday'].unique(), reverse=True)
        else:
            matchdays = ['--']

        selected_matchday = st.selectbox("Matchday", matchdays)

    # Dropdown for Fixture
    with col3:
        if selected_matchday != '--':
            df_matches = df_season[df_season['Matchday'] == selected_matchday]
            match_options = ['--'] + df_matches.apply(
                lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1).tolist()
        else:
            match_options = ['--']
            df_matches = pd.DataFrame()  # Empty DataFrame if no matchday is selected

        selected_match = st.selectbox("Fixture", match_options)

    # Display team logos and matchup info if a valid fixture is selected
    if selected_season != '--' and selected_matchday != '--' and selected_match != '--':
        selected_match_row = df_matches[
            df_matches.apply(lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1) == selected_match
        ].iloc[0]

        home_team = selected_match_row['Home Team']
        away_team = selected_match_row['Away Team']
        home_team_tag = selected_match_row['Home Tag']
        away_team_tag = selected_match_row['Away Tag']
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

        # Resize images based on target area for consistent size
        target_area = 10000  # You can adjust this value to control the overall size
        home_logo_resized = resize_image(home_logo, target_area)
        away_logo_resized = resize_image(away_logo, target_area)

        col1, col2, col3 = st.columns([1, 3, 1])

        with col1:
            st.markdown("<div style='display: flex; align-items: center; height: 100%; justify-content: center;'>", unsafe_allow_html=True)
            st.image(home_logo_resized, use_column_width=False)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
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

        with col3:
            st.markdown("<div style='display: flex; align-items: center; height: 100%; justify-content: center;'>", unsafe_allow_html=True)
            st.image(away_logo_resized, use_column_width=False)
            st.markdown("</div>", unsafe_allow_html=True)

        # Display match details
        match_date = pd.to_datetime(match_date_str)
        match_time_formatted = pd.to_datetime(match_time).strftime('%H:%M')  # Formats as HH:MM
        match_date_formatted = match_date.strftime('%A, %d. %B, %Y')

        st.markdown(
            f"<div style='text-align: center; margin-top: -40px;'>{match_date_formatted} @ {match_time_formatted}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='text-align: center; margin-top: -35px;'>{stadium}, {location}</div>",
            unsafe_allow_html=True
        )

        # Teams Overview Section
        st.subheader("Teams Overview")

        # Get team data for both teams
        def get_team_data(team_tag, matchday):
            previous_matchday = matchday - 1
            earlier_matchday = matchday - 2  # For movement comparison

            if previous_matchday <= 0:
                return {
                    'rank': '--',
                    'points': '--',
                    'goals_scored': '--',
                    'goals_conceded': '--',
                    'gd': '--',
                    'previous_rank': '--',
                    'games': 0,
                    'wins': 0,
                    'ties': 0,
                    'losses': 0
                }

            # Filter up to the previous matchday
            df_previous = df_season[df_season['Matchday'] <= previous_matchday]
            df_earlier = df_season[df_season['Matchday'] <= earlier_matchday]

            # Calculate the stats up to the previous matchday
            games = len(df_previous[(df_previous['Home Tag'] == team_tag) | (df_previous['Away Tag'] == team_tag)])
            wins = len(df_previous[((df_previous['Home Tag'] == team_tag) & (df_previous['Home Goals'] > df_previous['Away Goals'])) |
                                   ((df_previous['Away Tag'] == team_tag) & (df_previous['Away Goals'] > df_previous['Home Goals']))])
            ties = len(df_previous[((df_previous['Home Tag'] == team_tag) | (df_previous['Away Tag'] == team_tag)) & 
                                   (df_previous['Home Goals'] == df_previous['Away Goals'])])
            losses = games - (wins + ties)

            # Get current rank and points from the previous matchday
            previous_match_row_home = df_previous[(df_previous['Matchday'] == previous_matchday) & (df_previous['Home Tag'] == team_tag)]
            previous_match_row_away = df_previous[(df_previous['Matchday'] == previous_matchday) & (df_previous['Away Tag'] == team_tag)]

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

            # Get previous rank for movement calculation
            earlier_match_row_home = df_earlier[(df_earlier['Matchday'] == earlier_matchday) & (df_earlier['Home Tag'] == team_tag)]
            earlier_match_row_away = df_earlier[(df_earlier['Matchday'] == earlier_matchday) & (df_earlier['Away Tag'] == team_tag)]

            if not earlier_match_row_home.empty:
                previous_rank = earlier_match_row_home.iloc[0]['Home Team Rank']
            elif not earlier_match_row_away.empty:
                previous_rank = earlier_match_row_away.iloc[0]['Away Team Rank']
            else:
                previous_rank = '--'

            return {
                'rank': rank,
                'points': points,
                'goals_scored': goals_scored,
                'goals_conceded': goals_conceded,
                'gd': gd,
                'previous_rank': previous_rank,
                'games': games,
                'wins': wins,
                'ties': ties,
                'losses': losses
            }

        # Calculate movement in the league table
        def get_movement(rank, previous_rank):
            if previous_rank == '--' or rank == '--':
                return '--'
            elif int(rank) < int(previous_rank):
                return '⬆️'  # Moved up
            elif int(rank) > int(previous_rank):
                return '⬇️'  # Moved down
            else:
                return '⏺️'  # Stayed the same

        # Get the data for both teams
        home_data = get_team_data(home_team_tag, matchday)
        away_data = get_team_data(away_team_tag, matchday)

        home_data['movement'] = get_movement(home_data['rank'], home_data['previous_rank'])
        away_data['movement'] = get_movement(away_data['rank'], away_data['previous_rank'])

        # Function to display the header row
        def display_header():
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

        # Function to display the team data
        def display_team_data(team_data, team_name, team_tag):
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([1.1, 1, 5, 1.5, 0.75, 0.75, 0.75, 1.75, 1, 1.5])

            with col1:
                st.write(f"{team_data['rank']}")
            
            with col2:
                st.write(team_data['movement'])
            
            with col3:
                st.write(f"{team_name}")
            
            with col4:
                st.write(f"{team_data['games']}")
            
            with col5:
                st.write(f"{team_data['wins']}")
            
            with col6:
                st.write(f"{team_data['ties']}")
            
            with col7:
                st.write(f"{team_data['losses']}")
            
            with col8:
                st.write(f"{team_data['goals_scored']} : {team_data['goals_conceded']}")
            
            with col9:
                st.write(f"{team_data['gd']}")
            
            with col10:
                st.write(f"**{team_data['points']}**")

        # Display the header
        display_header()

        # Determine the top and bottom teams based on rank
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
            bottom_team_tag = home_team_tag

        # Display the teams sorted by rank
        display_team_data(top_team_data, top_team_name, top_team_tag)
        display_team_data(bottom_team_data, bottom_team_name, bottom_team_tag)

    # Return the selected values and the filtered matches DataFrame
    return selected_season, selected_matchday, selected_match, df_matches