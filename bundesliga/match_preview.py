import streamlit as st
import pandas as pd
from PIL import Image
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

    # Ensure that the selection is valid before proceeding
    if selected_season == '--' or selected_matchday == '--' or selected_match == '--':
        return selected_season, selected_matchday, selected_match, None

    # Fetch the selected match row
    selected_match_row = df_matches[
        df_matches.apply(lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1) == selected_match
    ].iloc[0]

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

    # Load the stadium image and Bundesliga logo
    stadium_image_path = f"data/logos/stadiums/{home_team_tag}_stadium.png"
    bundesliga_logo_path = "data/logos/team_logos/Bundesliga.svg.png"

    stadium_image = load_image(stadium_image_path)
    bundesliga_logo = load_image(bundesliga_logo_path)

    # Resize the images for better display
    stadium_image_resized = resize_image(stadium_image, 5000)  # Smaller area for better alignment
    bundesliga_logo_resized = resize_image(bundesliga_logo, 3000)  # Smaller area for better alignment

    # Display the match outcome or input fields and add the images to the sides
    row2_col1, row2_col2, row2_col3 = st.columns([1, 2, 1])

    with row2_col1:
        st.markdown("<div style='display: flex; align-items: center; height: 100%; justify-content: flex-end;'>", unsafe_allow_html=True)
        st.image(stadium_image_resized, use_column_width=False)
        st.markdown("</div>", unsafe_allow_html=True)

    with row2_col2:
        if selected_season == '2023/24':
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
                st.markdown("<div style='font-size: 30px;'>:</div>", unsafe_allow_html=True)
            with col2_right:
                away_goals = col2_right.number_input("", min_value=0, max_value=11, value=0, step=1, key="away_goals", format="%d")
        else:
            # Display the outcome for previous seasons
            match_outcome = f"{selected_match_row['Home Goals']} : {selected_match_row['Away Goals']}"
            st.markdown(
                f"<div style='text-align: center; font-size: 60px; font-family: Courier; color: #FFFF4F; margin-top: -10px;'>{match_outcome}</div>",
                unsafe_allow_html=True
            )

    with row2_col3:
        st.markdown("<div style='display: flex; align-items: center; height: 100%; justify-content: flex-start;'>", unsafe_allow_html=True)
        st.image(bundesliga_logo_resized, use_column_width=False)
        st.markdown("</div>", unsafe_allow_html=True)

    # Teams Overview Section
    st.subheader("Teams Overview")

    # Determine if the selected season is the current one (2023/24)
    is_current_season = selected_season == '2023/24'

    # Get team data for both teams
    def get_team_data(team_tag, matchday, is_current_season):
        if is_current_season:
            previous_matchday = matchday - 1
        else:
            previous_matchday = matchday

        earlier_matchday = previous_matchday - 1  # For movement comparison

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

        # Filter up to the appropriate matchday
        df_filtered = df_season[df_season['Matchday'] <= previous_matchday]
        df_earlier = df_season[df_season['Matchday'] <= earlier_matchday]

        # Calculate the stats up to the appropriate matchday
        games = len(df_filtered[(df_filtered['Home Tag'] == team_tag) | (df_filtered['Away Tag'] == team_tag)])
        wins = len(df_filtered[((df_filtered['Home Tag'] == team_tag) & (df_filtered['Home Goals'] > df_filtered['Away Goals'])) |
                                ((df_filtered['Away Tag'] == team_tag) & (df_filtered['Away Goals'] > df_filtered['Home Goals']))])
        ties = len(df_filtered[((df_filtered['Home Tag'] == team_tag) | (df_filtered['Away Tag'] == team_tag)) & 
                                (df_filtered['Home Goals'] == df_filtered['Away Goals'])])
        losses = games - (wins + ties)

        # Get current rank and points from the appropriate matchday
        current_match_row_home = df_filtered[(df_filtered['Matchday'] == previous_matchday) & (df_filtered['Home Tag'] == team_tag)]
        current_match_row_away = df_filtered[(df_filtered['Matchday'] == previous_matchday) & (df_filtered['Away Tag'] == team_tag)]

        if not current_match_row_home.empty:
            row = current_match_row_home.iloc[0]
            rank = row['Home Team Rank']
            points = row['Home Team Points']
            goals_scored = row['Home Team Goals Scored']
            goals_conceded = row['Home Team Goals Conceded']
            gd = row['Home Team GD']
        else:
            row = current_match_row_away.iloc[0]
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
            'losses': losses,
            'team_tag': team_tag
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
    home_data = get_team_data(home_team_tag, matchday, is_current_season)
    away_data = get_team_data(away_team_tag, matchday, is_current_season)

    home_data['movement'] = get_movement(home_data['rank'], home_data['previous_rank'])
    away_data['movement'] = get_movement(away_data['rank'], away_data['previous_rank'])

    # Ensure better-ranked team is displayed on top
    if home_data['rank'] != '--' and away_data['rank'] != '--':
        if int(home_data['rank']) > int(away_data['rank']):
            # Swap data if away team is better ranked
            home_data, away_data = away_data, home_data

    # Display the Teams Overview table with a styled frame and logos
    display_styled_team_table(home_data, away_data, home_team, away_team)

    return selected_season, selected_matchday, selected_match, df_matches

# Utility function to convert an image to bytes (needed for displaying the image)
def image_to_bytes(image):
    import base64
    from io import BytesIO
    
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str

def display_styled_team_table(home_data, away_data, home_team, away_team):
    def get_team_logo_img_tag(team_tag):
        """Return an HTML image tag for the team logo."""
        logo_path = f"data/logos/team_logos/{team_tag}.svg.png"
        logo_img_tag = f'<img src="data:image/png;base64,{image_to_bytes(load_image(logo_path))}" style="max-width: 20px; max-height: 20px; vertical-align: middle;" />'
        return logo_img_tag

    # Generating HTML image tags for the home and away team logos
    home_logo_tag = get_team_logo_img_tag(home_data['team_tag'])
    away_logo_tag = get_team_logo_img_tag(away_data['team_tag'])

    st.markdown(
        """
        <style>
        .styled-table {
            border-collapse: collapse;
            margin: -5px 0;
            font-size: 0.9em;
            font-family: 'Sans-serif', Arial, Helvetica, sans-serif;
            width: 100%;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            border-radius: 15px;
            overflow: hidden;
            background-color: rgba(255, 255, 255, 0.5); /* Background color for data rows with 50% transparency */
            border: 2px solid #696969; /* Border around the entire table */
        }

        .styled-table thead tr {
            background-color: rgba(14, 17, 23, 0.70); /* Background color for the header row with 25% transparency */
            color: #ffffff; /* Text color for the header row */
            text-align: left;
        }

        .styled-table th,
        .styled-table td {
            padding: 12px 15px;
            text-align: center;
        }

        .styled-table tbody tr {
            background-color: rgba(14, 17, 23, 0.35); /* Background color for data rows with 50% transparency */
            border-bottom: 1px solid rgba(97, 101, 114, 0.9); /* Matching border for rows */
        }

        .styled-table tbody tr:last-of-type {
            border-bottom: 2px solid rgba(97, 101, 114, 0.9);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th></th>
                    <th>Team</th>
                    <th>Games</th>
                    <th>W</th>
                    <th>T</th>
                    <th>L</th>
                    <th>Goals</th>
                    <th>GD</th>
                    <th>Points</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{home_data['rank']}</td>
                    <td>{home_data['movement']}</td>
                    <td>{home_logo_tag} {home_data['team_tag']}</td>
                    <td>{home_data['games']}</td>
                    <td>{home_data['wins']}</td>
                    <td>{home_data['ties']}</td>
                    <td>{home_data['losses']}</td>
                    <td>{home_data['goals_scored']} : {home_data['goals_conceded']}</td>
                    <td>{home_data['gd']}</td>
                    <td><b>{home_data['points']}</b></td>
                </tr>
                <tr>
                    <td>{away_data['rank']}</td>
                    <td>{away_data['movement']}</td>
                    <td>{away_logo_tag} {away_data['team_tag']}</td>
                    <td>{away_data['games']}</td>
                    <td>{away_data['wins']}</td>
                    <td>{away_data['ties']}</td>
                    <td>{away_data['losses']}</td>
                    <td>{away_data['goals_scored']} : {away_data['goals_conceded']}</td>
                    <td>{away_data['gd']}</td>
                    <td><b>{away_data['points']}</b></td>
                </tr>
            </tbody>
        </table>
        """,
        unsafe_allow_html=True
    )

# Utility function to convert an image to bytes (needed for displaying the image)
def image_to_bytes(image):
    import base64
    from io import BytesIO
    
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str