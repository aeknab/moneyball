import streamlit as st
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

plt.style.use('fivethirtyeight')

# Load the dataset
@st.cache_data
def load_data():
    return pd.read_csv('/Users/andreas/Desktop/02 - Moneyball/Datasets/03 - Bundesliga Data/BuLi All Seasons.csv')

df = load_data()

# Load the color codes
@st.cache_data
def load_colors():
    return pd.read_csv('/Users/andreas/Desktop/02 - Moneyball/Just the Tipp/06 - Logos/Color Codes.csv')

colors = load_colors()

# Define the path to the team logos directory on your laptop
LOGO_DIR = '/Users/andreas/Desktop/02 - Moneyball/Just the Tipp/06 - Logos/01 - Bundesliga'

# Function to load and resize the team logos
@st.cache_data
def load_image(image_path):
    return Image.open(image_path)

def resize_image(image, max_width, max_height):
    aspect_ratio = image.width / image.height
    if aspect_ratio > 1:
        new_width = min(image.width, max_width)
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = min(image.height, max_height)
        new_width = int(new_height * aspect_ratio)
    resized_image = image.resize((new_width, new_height))
    return resized_image

# Function to get last 5 matches
def get_last_5_matches(df_season, team, matchday):
    previous_matches = df_season[((df_season['Home Team'] == team) | (df_season['Away Team'] == team)) & 
                                 (df_season['Matchday'] < matchday)].sort_values(by='Matchday', ascending=False).head(5)
    
    match_tags = []
    results = []
    outcomes = []
    
    for index, match in previous_matches.iterrows():
        if match['Home Team'] == team:
            opponent = match['Away Tag']
            score = f"{match['Home Goals']}:{match['Away Goals']}"
            if match['Home Goals'] > match['Away Goals']:
                result = 'W'
            elif match['Home Goals'] < match['Away Goals']:
                result = 'L'
            else:
                result = 'T'
        else:
            opponent = match['Home Tag']
            score = f"{match['Away Goals']}:{match['Home Goals']}"
            if match['Away Goals'] > match['Home Goals']:
                result = 'W'
            elif match['Away Goals'] < match['Home Goals']:
                result = 'L'
            else:
                result = 'T'
        
        match_tags.append(opponent)
        results.append(result)
        outcomes.append(score)
    
    total_matches = len(previous_matches)
    return match_tags, results, outcomes, total_matches

# Function to get the color code for a team
def get_team_colors(team_tag, color_codes_df):
    team_data = color_codes_df[color_codes_df['Tag'] == team_tag]
    if not team_data.empty:
        primary_color = team_data['Primary'].values[0]
        secondary_color = team_data['Secondary'].values[0]
        # Optionally, you could also use the tertiary color if needed:
        # tertiary_color = team_data['Tertiary'].values[0]
        return primary_color, secondary_color
    return '#000000', '#000000'  # Default to black if team not found

# Function to get last 10 meetings
def get_last_10_meetings(df, home_team_tag, away_team_tag, color_codes_df, current_matchday, current_season):
    # Filter matches between the two teams
    matches_between_teams = df[
        ((df['Home Tag'] == home_team_tag) & (df['Away Tag'] == away_team_tag)) | 
        ((df['Home Tag'] == away_team_tag) & (df['Away Tag'] == home_team_tag))
    ]
    
    # Further filter to exclude current and future matchdays in the current season
    matches_between_teams = matches_between_teams[
        ~((matches_between_teams['Season'] == current_season) & (matches_between_teams['Matchday'] >= current_matchday))
    ].sort_values(by='Match Date', ascending=False).head(10)
    
    team1_wins = 0
    team2_wins = 0
    draws = 0

    total_matches = len(matches_between_teams)

    for _, match in matches_between_teams.iterrows():
        if match['Home Tag'] == home_team_tag:
            if match['Home Goals'] > match['Away Goals']:
                team1_wins += 1
            elif match['Home Goals'] < match['Away Goals']:
                team2_wins += 1
            else:
                draws += 1
        elif match['Home Tag'] == away_team_tag:
            if match['Home Goals'] > match['Away Goals']:
                team2_wins += 1
            elif match['Home Goals'] < match['Away Goals']:
                team1_wins += 1
            else:
                draws += 1

    # Get the colors for the home and away teams using the tags
    home_primary, home_secondary = get_team_colors(home_team_tag, color_codes_df)
    away_primary, away_secondary = get_team_colors(away_team_tag, color_codes_df)
    
    # Use the primary color of the away team by default
    away_color = away_primary
    
    return team1_wins, team2_wins, draws, home_primary, away_color, total_matches

# Function to plot last 10 meetings
def plot_last_10_meetings(df, home_team_tag, away_team_tag, color_codes_df, current_matchday, current_season):
    team1_wins, team2_wins, draws, home_color, away_color, total_matches = get_last_10_meetings(
        df, home_team_tag, away_team_tag, color_codes_df, current_matchday, current_season
    )
    
    # Update the header to reflect the actual number of meetings
    st.subheader(f"Last {total_matches} Meeting{'s' if total_matches > 1 else ''}")
    
    if total_matches > 0:
        # Calculate proportions
        proportions = [team1_wins / total_matches, draws / total_matches, team2_wins / total_matches]
        
        # Get secondary colors for shading
        home_primary, home_secondary = get_team_colors(home_team_tag, color_codes_df)
        away_primary, away_secondary = get_team_colors(away_team_tag, color_codes_df)
        
        # Create horizontal stacked bar chart with shading
        fig, ax = plt.subplots(figsize=(8, 2))  # Keep the overall figure size the same
        
        # Adjust the 'height' parameter to increase the bar thickness
        ax.barh(0, proportions[0], color=home_primary, hatch='///', edgecolor=home_secondary, height=1)
        ax.barh(0, proportions[1], left=proportions[0], color='#BBBBBB', hatch='///', edgecolor='#FFFFFF', height=1)
        ax.barh(0, proportions[2], left=proportions[0] + proportions[1], color=away_primary, hatch='///', edgecolor=away_secondary, height=1)

        # Remove axes and ticks
        ax.axis('off')
        
        # Load and resize team logos
        home_logo_path = f"/Users/andreas/Desktop/02 - Moneyball/Just the Tipp/06 - Logos/01 - Bundesliga/{home_team_tag}.svg.png"
        away_logo_path = f"/Users/andreas/Desktop/02 - Moneyball/Just the Tipp/06 - Logos/01 - Bundesliga/{away_team_tag}.svg.png"
        
        home_logo = load_image(home_logo_path)
        away_logo = load_image(away_logo_path)
        
        # Ensure the images are in RGBA mode
        home_logo = home_logo.convert("RGBA")
        away_logo = away_logo.convert("RGBA")
        
        # Resize logos for the legend
        max_width = 30  # Adjust as needed
        max_height = 30  # Adjust as needed
        
        home_logo_resized = resize_image(home_logo, max_width, max_height)
        away_logo_resized = resize_image(away_logo, max_width, max_height)
     
        # Convert PIL images to arrays for plotting in the legend
        home_logo_array = np.array(home_logo_resized)
        away_logo_array = np.array(away_logo_resized)
        
        # Use AnnotationBbox to place logos to the left of the text
        ab_home = AnnotationBbox(OffsetImage(home_logo_array, zoom=0.6), (0.02, -0.55), frameon=False, box_alignment=(0.5, 0.5))
        ab_away = AnnotationBbox(OffsetImage(away_logo_array, zoom=0.6), (0.98, -0.55), frameon=False, box_alignment=(0.5, 0.5))
        
        ax.add_artist(ab_home)
        ax.add_artist(ab_away)
        
        # Adding text labels for the logos and ties
        ax.text(0.05, -0.55, f'{team1_wins} Wins', ha='left', va='center', fontsize=10)   # Home team wins aligned to the left
        ax.text(0.5, -0.55, f'{draws} Ties', ha='center', va='center', fontsize=10)        # Ties centered
        ax.text(0.95, -0.55, f'{team2_wins} Wins', ha='right', va='center', fontsize=10)   # Away team wins aligned to the right

        # Add more space between the bar and the legend
        plt.subplots_adjust(bottom=0.6)  # Increased bottom space to avoid overlap

        # Display the chart
        st.pyplot(fig)
    else:
        st.write(f"No previous matches between {home_team_tag} and {away_team_tag}.")
        
# Function to generate the form guide donut chart
def generate_form_guide(team, matchday, df_season):
    # Check if there are previous matches
    if matchday <= 1:
        st.write(f"No previous match data available for {team}.")
        return

    previous_matches = df_season[
        (df_season['Matchday'] < matchday) &
        ((df_season['Home Team'] == team) | (df_season['Away Team'] == team))
    ]

    # If no previous matches, display a message
    if previous_matches.empty:
        st.write(f"No previous match data available for {team}.")
        return

    # Calculate Wins, Ties, and Losses
    wins = len(previous_matches[
        ((previous_matches['Home Team'] == team) & (previous_matches['Home Goals'] > previous_matches['Away Goals'])) |
        ((previous_matches['Away Team'] == team) & (previous_matches['Away Goals'] > previous_matches['Home Goals']))
    ])

    ties = len(previous_matches[previous_matches['Home Goals'] == previous_matches['Away Goals']])

    losses = len(previous_matches[
        ((previous_matches['Home Team'] == team) & (previous_matches['Home Goals'] < previous_matches['Away Goals'])) |
        ((previous_matches['Away Team'] == team) & (previous_matches['Away Goals'] < previous_matches['Home Goals']))
    ])

    # Calculate percentages
    total_games = wins + ties + losses
    if total_games > 0:
        win_pct = wins / total_games * 100
        tie_pct = ties / total_games * 100
        loss_pct = losses / total_games * 100
    else:
        win_pct = tie_pct = loss_pct = 0

    # Donut chart without the detached slice
    labels = ['Wins', 'Ties', 'Losses']
    sizes = [wins, ties, losses]
    colors = ['#a8e6a1', '#c4c4c4', '#ff9999']

    fig, ax = plt.subplots()
    wedges, texts = ax.pie(sizes, labels=None, colors=colors, startangle=140, pctdistance=0.85)

    # Create a donut shape by adding a circle at the center
    center_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig.gca().add_artist(center_circle)
    ax.axis('equal')

    # Create a legend below the chart
    legend_labels = [f'{label} ({size}) - {pct:.1f}%' for label, size, pct in zip(labels, sizes, [win_pct, tie_pct, loss_pct])]
    ax.legend(wedges, legend_labels, loc='center', bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=False)

    # Display the donut chart
    st.pyplot(fig)

    # Get average goals and rankings
    if total_games > 0:
        avg_goals_scored = (previous_matches[previous_matches['Home Team'] == team]['Home Goals'].mean() +
                            previous_matches[previous_matches['Away Team'] == team]['Away Goals'].mean())
        avg_goals_conceded = (previous_matches[previous_matches['Home Team'] == team]['Away Goals'].mean() +
                              previous_matches[previous_matches['Away Team'] == team]['Home Goals'].mean())

        # Get the most recent match row to get the offensive and defensive rankings
        latest_match_row = previous_matches.iloc[-1]
        offensive_rank = latest_match_row['Home Team Offensive Ranking'] if latest_match_row['Home Team'] == team else latest_match_row['Away Team Offensive Ranking']
        defensive_rank = latest_match_row['Home Team Defensive Ranking'] if latest_match_row['Home Team'] == team else latest_match_row['Away Team Defensive Ranking']

        # Display statistics in the center of the donut chart
        st.write(f"**Average Goals Scored:** {avg_goals_scored:.2f}")
        st.write(f"**Average Goals Conceded:** {avg_goals_conceded:.2f}")
        st.write(f"**Offensive Ranking:** {offensive_rank}")
        st.write(f"**Defensive Ranking:** {defensive_rank}")
    else:
        st.write("No data available for this matchday.")

# Set up the Streamlit app
st.title("Bundesliga Dashboard")
st.header("Matchday Preview")

# Initialize session state with default values if not already done
if 'selected_season' not in st.session_state:
    st.session_state.selected_season = '--'
if 'selected_matchday' not in st.session_state:
    st.session_state.selected_matchday = '--'
if 'selected_match' not in st.session_state:
    st.session_state.selected_match = '--'

# Layout for filters: Place them side by side
col1, col2, col3 = st.columns(3)

# Filter by Season
with col1:
    seasons = ['--'] + sorted(df['Season'].unique(), reverse=True)
    selected_season = st.selectbox(
        "Season", seasons, index=seasons.index(st.session_state.selected_season)
    )

    # Update session state if the season selection has changed
    if selected_season != st.session_state.selected_season:
        st.session_state.selected_season = selected_season
        st.session_state.selected_matchday = '--'  # Reset Matchday when season changes
        st.session_state.selected_match = '--'     # Reset Fixture when season changes

# Filter by Matchday
with col2:
    if st.session_state.selected_season != '--':
        df_season = df[df['Season'] == st.session_state.selected_season]
        matchdays = ['--'] + sorted(df_season['Matchday'].unique(), reverse=True)
        selected_matchday = st.selectbox(
            "Matchday", matchdays, index=matchdays.index(st.session_state.selected_matchday)
        )

        # Update session state if the matchday selection has changed
        if selected_matchday != st.session_state.selected_matchday:
            st.session_state.selected_matchday = selected_matchday
            st.session_state.selected_match = '--'  # Reset Fixture when matchday changes
    else:
        st.write("Please select a season first.")

# Filter by Fixture
with col3:
    if st.session_state.selected_matchday != '--':
        df_matches = df_season[df_season['Matchday'] == st.session_state.selected_matchday]
        df_matches_sorted = df_matches.sort_values(by=['Match Date', 'Match Time'])
        match_options = ['--'] + df_matches_sorted.apply(
            lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1).tolist()
        selected_match = st.selectbox(
            "Fixture", match_options, index=match_options.index(st.session_state.selected_match)
        )

        # Update session state if the fixture selection has changed
        if selected_match != st.session_state.selected_match:
            st.session_state.selected_match = selected_match
    else:
        st.write("Please select a matchday first.")

# Ensure both matchday and fixture are selected before proceeding
if st.session_state.selected_matchday != '--' and st.session_state.selected_match != '--':
    # Extract the team tags and match details
    selected_match_row = df_matches_sorted[df_matches_sorted.apply(
        lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1
    ) == st.session_state.selected_match].iloc[0]
    
    home_team_tag = selected_match_row['Home Tag']
    away_team_tag = selected_match_row['Away Tag']
    match_date_str = selected_match_row['Match Date']
    match_time_str = selected_match_row['Match Time']
    stadium = selected_match_row['Stadium']
    location = selected_match_row['Location']

    # Construct the paths to the team logos
    home_logo_path = os.path.join(LOGO_DIR, f"{home_team_tag}.svg.png")
    away_logo_path = os.path.join(LOGO_DIR, f"{away_team_tag}.svg.png")

    # Load and resize the logos
    try:
        home_logo = load_image(home_logo_path)
        away_logo = load_image(away_logo_path)
        home_logo_resized = resize_image(home_logo, 100, 100)
        away_logo_resized = resize_image(away_logo, 100, 100)
    except FileNotFoundError as e:
        st.error(f"Error loading team logos: {e}")
        st.stop()

    # Display logos and match details
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.image(home_logo_resized, use_column_width=False)
    with col2:
        st.markdown(f"<div style='text-align: center; font-size: 24px;'><b>{selected_match_row['Home Team']}</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 20px;'>vs.</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 24px;'><b>{selected_match_row['Away Team']}</b></div>", unsafe_allow_html=True)
    with col3:
        st.image(away_logo_resized, use_column_width=False)

    # Convert the date string to a datetime object
    match_date = pd.to_datetime(match_date_str)

    # Convert the time string to a datetime object and format it
    match_time = pd.to_datetime(match_time_str).strftime('%H:%M')  # Formats as HH:MM

    # Format the date
    match_date_formatted = match_date.strftime('%A, %d. %B, %Y')

    # Display the first section with date, time, and location
    st.markdown(f"<div style='text-align: center;'>{match_date_formatted} @ {match_time}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center;'>{stadium}, {location}</div>", unsafe_allow_html=True)

# Function to extract team data from the previous matchday
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

# Ensure both matchday and fixture are selected before proceeding
if selected_matchday != '--' and selected_match != '--':
    # Extract the team tags and match details
    selected_match_row = df_matches_sorted[df_matches_sorted.apply(
        lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1
    ) == selected_match].iloc[0]
    
    home_team_tag = selected_match_row['Home Tag']
    away_team_tag = selected_match_row['Away Tag']
    match_date_str = selected_match_row['Match Date']
    match_time_str = selected_match_row['Match Time']
    stadium = selected_match_row['Stadium']
    location = selected_match_row['Location']

    # Construct the paths to the team logos
    home_logo_path = os.path.join(LOGO_DIR, f"{home_team_tag}.svg.png")
    away_logo_path = os.path.join(LOGO_DIR, f"{away_team_tag}.svg.png")

    # Load and resize the logos
    try:
        home_logo = load_image(home_logo_path)
        away_logo = load_image(away_logo_path)
        home_logo_resized = resize_image(home_logo, 100, 100)
        away_logo_resized = resize_image(away_logo, 100, 100)
    except FileNotFoundError as e:
        st.error(f"Error loading team logos: {e}")
        st.stop()

    # Display logos and match details
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.image(home_logo_resized, use_column_width=False)
    with col2:
        st.markdown(f"<div style='text-align: center; font-size: 24px;'><b>{selected_match_row['Home Team']}</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 20px;'>vs.</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 24px;'><b>{selected_match_row['Away Team']}</b></div>", unsafe_allow_html=True)
    with col3:
        st.image(away_logo_resized, use_column_width=False)

    # Convert the date string to a datetime object
    match_date = pd.to_datetime(match_date_str)

    # Convert the time string to a datetime object and format it
    match_time = pd.to_datetime(match_time_str).strftime('%H:%M')  # Formats as HH:MM

    # Format the date
    match_date_formatted = match_date.strftime('%A, %d. %B, %Y')

    # Display the first section with date, time, and location
    st.markdown(f"<div style='text-align: center;'>{match_date_formatted} @ {match_time}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center;'>{stadium}, {location}</div>", unsafe_allow_html=True)

    # Get team data for both teams
    home_data = get_team_data(home_team_tag, matchday)
    away_data = get_team_data(away_team_tag, matchday)

    # If there's no previous matchday data (e.g., Matchday 1), fill with placeholders
    if home_data['rank'] == '--' or away_data['rank'] == '--':
        home_data['movement'] = '--'
        away_data['movement'] = '--'
    else:
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
        
    # Display the header
    st.subheader("Teams Overview")
    display_header()
        
    # Function to calculate team statistics (games, wins, ties, losses)
    def calculate_team_stats(df_season, team):
            df_filtered = df_season[df_season['Matchday'] < matchday]
            games = len(df_filtered[(df_filtered['Home Team'] == team) | (df_filtered['Away Team'] == team)])
            wins = len(df_filtered[
                ((df_filtered['Home Team'] == team) & (df_filtered['Home Goals'] > df_filtered['Away Goals'])) |
                ((df_filtered['Away Team'] == team) & (df_filtered['Away Goals'] > df_filtered['Home Goals']))
            ])
            ties = len(df_filtered[
                ((df_filtered['Home Team'] == team) | (df_filtered['Away Team'] == team)) & 
                (df_filtered['Home Goals'] == df_filtered['Away Goals'])
            ])
            losses = games - (wins + ties)

            return games, wins, ties, losses
        
    # Function to display the team data
    def display_team_data(df_season, team_data, team_name, team_tag):
            games, wins, ties, losses = calculate_team_stats(df_season, team_name)
            
            # Load and resize the team logo
            team_logo_path = f"/path/to/{team_tag}.svg.png"
            team_logo = load_image(team_logo_path)
        
            max_width = 25  # Adjust as needed for Teams Overview
            max_height = 25  # Adjust as needed for Teams Overview
        
            team_logo_resized = resize_image(team_logo, max_width, max_height)
        
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([1.1, 1, 5, 1.5, 0.75, 0.75, 0.75, 1.75, 1, 1.5])
            
            with col1:
                st.write(f"{team_data['rank']}")
            
            with col2:
                st.write(f"{team_data['movement']}")
            
            with col3:
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

    # Display the teams sorted by rank
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

    # Function to resize images for display in charts
    def resize_image_to_bounding_box(image, target_width, target_height):
            # Convert image to RGBA to ensure compatibility
            image = image.convert("RGBA")
            
            # Calculate the aspect ratio
            aspect_ratio = image.width / image.height
            
            # Determine the new dimensions based on the aspect ratio
            if aspect_ratio > 1:  # Wider than tall
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            else:  # Taller than wide, or square
                new_height = target_height
                new_width = int(target_height * aspect_ratio)
            
            # Resize the image to fit within the bounding box
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            return resized_image
        
    # Sixth Section - League Table
    st.subheader("League Table")
        
    # Filter the dataset for all matchdays up to the selected fixture
    df_season_before_matchday = df[(df['Matchday'] < matchday) & (df['Season'] == selected_season)]
        
    if not df_season_before_matchday.empty:
            # Extract the points for each team up to the selected matchday
            points_data = []
        
            # Collect points from the last matchday only
            df_last_md = df_season_before_matchday[df_season_before_matchday['Matchday'] == matchday - 1]
        
            for index, row in df_last_md.iterrows():
                points_data.append((row['Home Tag'], row['Home Team Points']))
                points_data.append((row['Away Tag'], row['Away Team Points']))
        
            # Convert to DataFrame and ensure there are no duplicates
            df_points = pd.DataFrame(points_data, columns=['Team Tag', 'Points']).drop_duplicates(subset=['Team Tag'])
        
            # Sort the DataFrame by points to represent the league table
            df_points = df_points.sort_values(by='Points', ascending=False)

            # Create the bar chart
            fig, ax = plt.subplots(figsize=(14, 10))  # Adjust size if necessary
        
            # Adjust the thickness and spacing of the bars
            bar_height = 2
            spacing = 2.5
        
            for i, (team_tag, points) in enumerate(zip(df_points['Team Tag'], df_points['Points'])):
                primary_color, secondary_color = get_team_colors(team_tag, colors)
                ax.barh(i * spacing, points, color=primary_color, hatch='///', edgecolor=secondary_color, height=bar_height)
        
                # Load and resize the team logo to fit within a bounding box
                team_logo_path = f"/path/to/{team_tag}.svg.png"
        
                if os.path.exists(team_logo_path):
                    team_logo = Image.open(team_logo_path)
                    team_logo_resized = resize_image_to_bounding_box(team_logo, target_width=30, target_height=30)
                    logo = OffsetImage(np.array(team_logo_resized), zoom=1)  # No additional zoom, use as is
                    ab = AnnotationBbox(logo, (points + 1, i * spacing), frameon=False, box_alignment=(0, 0.5))  # Adjust space after the bar
                    ax.add_artist(ab)
                else:
                    st.warning(f"Logo for {team_tag} not found at {team_logo_path}")
        
            # Replace team tags with ranks (1-18) on the y-axis
            ax.set_yticks([i * spacing for i in range(len(df_points))])
            ax.set_yticklabels([f'{rank}' for rank in range(1, len(df_points) + 1)])
        
            # Invert y-axis to have the top team at the top
            ax.invert_yaxis()
        
            # Set the x-axis range and labels
            ax.set_xlim(0, 100)  # Adjust x-axis to a reasonable range for points (e.g., 0-100)
            ax.set_xlabel('Points')
            ax.set_title(f'Bundesliga League Table After Matchday {matchday - 1} ({selected_season})')
        
            # Display the chart
            st.pyplot(fig)
    else:
            st.write("No data available for league table.")

    # Seventh Section - Bump Chart
    st.subheader("Bump Chart")
        
    if not df_season_before_matchday.empty:
            # Initialize a DataFrame to hold the rankings for each matchday
            rankings = []
        
            # Iterate through each matchday before the selected fixture
            for md in range(1, matchday):
                df_md = df_season_before_matchday[df_season_before_matchday['Matchday'] == md]
        
                # Collect the ranks for both the home and away teams
                for index, row in df_md.iterrows():
                    rankings.append({'Team Tag': row['Home Tag'], 'Rank': row['Home Team Rank'], 'Matchday': md})
                    rankings.append({'Team Tag': row['Away Tag'], 'Rank': row['Away Team Rank'], 'Matchday': md})
        
            # Convert the rankings list to a DataFrame
            df_rankings = pd.DataFrame(rankings)
        
            # Pivot the data to have matchdays as columns and teams as rows
            df_bump = df_rankings.pivot(index='Team Tag', columns='Matchday', values='Rank')

            # Plot the bump chart
            fig, ax = plt.subplots(figsize=(14, 10))
        
            # Iterate through each team and plot their rank over the matchdays with primary color
            for team_tag in df_bump.index:
                primary_color, _ = get_team_colors(team_tag, colors)  # Only use the primary color
                ax.plot(df_bump.columns, df_bump.loc[team_tag], marker='o', color=primary_color, label=team_tag)
        
                # Add team logos at the end of the line
                team_logo_path = f"/path/to/{team_tag}.svg.png"
                
                if os.path.exists(team_logo_path):
                    team_logo = Image.open(team_logo_path)
                    team_logo_resized = resize_image_to_bounding_box(team_logo, target_width=30, target_height=30)
                    end_x = df_bump.columns[-1]
                    end_y = df_bump.loc[team_tag].iloc[-1]
                    logo = OffsetImage(np.array(team_logo_resized), zoom=1)  # Use as is after resizing
                    ab = AnnotationBbox(logo, (end_x + 0.5, end_y), frameon=False, box_alignment=(0, 0.5))  # Adjust spacing as needed
                    ax.add_artist(ab)

            # Customize the chart
            ax.set_xlim(0.5, 34)  # Add buffer space on the left (starts at 0.5 instead of 1)
        
            # Set y-ticks from 1 to 18
            ax.set_yticks(range(1, 19))
            ax.set_yticklabels(range(1, 19))
        
            # Invert y-axis so that 1 is at the top
            ax.invert_yaxis()
        
            # Set x-ticks for all 34 matchdays
            ax.set_xticks(range(1, 35))  # Display all matchdays
        
            # Set vertical grid lines every 5 matchdays
            ax.xaxis.set_major_locator(plt.MultipleLocator(5))
        
            # Add a thicker, dotted line at the halfway mark (between 17th and 18th matchday)
            ax.axvline(x=17.5, color='black', linestyle=':', linewidth=1.5)
        
            # Remove the y-axis label
            ax.set_ylabel('')
        
            ax.set_xlabel('Matchday')
            ax.set_title(f'Bundesliga Bump Chart: League Position by Matchday ({selected_season})')
        
            # Remove the legend
            ax.legend().set_visible(False)
        
            # Display the chart
            st.pyplot(fig)
    else:
            st.write("No data available for bump chart.")

    # Eighth Section - Kreuztabelle
    st.subheader("Kreuztabelle")
        
    # Mapping of team tags to cities
    team_cities = {
            'B04': 'Leverkusen',
            'BMG': 'Mönchengladbach',
            'BVB': 'Dortmund',
            'FCB': 'München',
            'FCA': 'Augsburg',
            'SCF': 'Freiburg',
            'KOE': 'Köln',
            'M05': 'Mainz',
            'RBL': 'Leipzig',
            'SGE': 'Frankfurt',
            'VFB': 'Stuttgart',
            'SVW': 'Bremen',
            'WOB': 'Wolfsburg',
            'FCU': 'Berlin',
            'BOC': 'Bochum',
            'HDH': 'Heidenheim',
            'D98': 'Darmstadt',
            'TSG': 'Hoffenheim',
            'MSV': 'Duisburg',
            'HSV': 'Hamburg',
            'H96': 'Hannover',
            'S04': 'Gelsenkirchen',
            'BSC': 'Berlin',
            'FCK': 'Kaiserslautern',
            'FCN': 'Nürnberg',
            'DSC': 'Bielefeld',
            'FCE': 'Cottbus',
            'ALE': 'Aachen',
            'KSC': 'Karlsruhe',
            'FCH': 'Rostock',
            'STP': 'St. Pauli',
            'SGF': 'Fürth',
            'F95': 'Düsseldorf',
            'EBS': 'Braunschweig',
            'SCP': 'Paderborn',
            'FCI': 'Ingolstadt',
            'KIE': 'Kiel'
        }
        
    # Filter the dataset for matches before the selected matchday and for the selected season
    df_past_matches = df[(df['Matchday'] < matchday) & (df['Season'] == selected_season)]
        
    # Get the list of unique team tags for the selected season, limited to the teams that have played in that season
    teams_in_season = sorted(
            pd.unique(df_past_matches[['Home Tag', 'Away Tag']].values.ravel('K'))
        )
        
    # Reorder teams by their city names
    teams_in_season_sorted = sorted(teams_in_season, key=lambda tag: team_cities.get(tag, ''))
        
    # Create an empty DataFrame for the Kreuztabelle with teams ordered by city
    kreuztabelle = pd.DataFrame('--', index=teams_in_season_sorted, columns=teams_in_season_sorted)

    # Populate the Kreuztabelle with results
    for _, match in df_past_matches.iterrows():
            home_team = match['Home Tag']
            away_team = match['Away Tag']
            home_goals = match['Home Goals']
            away_goals = match['Away Goals']
            
            kreuztabelle.loc[home_team, away_team] = f"{home_goals}:{away_goals}"
        
    # Set diagonal cells to NaN for greyed out effect (teams don't play themselves)
    for team in teams_in_season_sorted:
            kreuztabelle.loc[team, team] = np.nan
        
    # Plot the Kreuztabelle
    fig, ax = plt.subplots(figsize=(12, 12))
        
    # Create the table with the grid
    ax.matshow(kreuztabelle.isnull(), cmap="gray_r", aspect='auto')
    ax.grid(color='black', linestyle='-', linewidth=0.5)  # Add the grid lines
        
    # Add text annotations for the scores and color the cells based on the outcome
    for i in range(len(kreuztabelle.index)):
            for j in range(len(kreuztabelle.columns)):
                value = kreuztabelle.iloc[i, j]
                if pd.notna(value) and value != '--':  # Ensure value is not '--'
                    home_goals, away_goals = map(int, value.split(':'))
                    if home_goals > away_goals:
                        color = 'lightgreen'
                    elif home_goals < away_goals:
                        color = 'lightyellow'
                    else:
                        color = 'lightgrey'
                    
                    ax.add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, color=color))
                    ax.text(j, i, value, ha='center', va='center', color="black")

    # Adjust plot limits to make space for logos
    ax.set_xlim(-1.5, len(kreuztabelle.columns) + 0.5)
    ax.set_ylim(len(kreuztabelle.index) + 0.5, -1.5)  # Invert y-axis
        
    # Replace team tags with logos
    def add_logo_at_position(ax, team_tag, x, y, box_alignment=(0.5, 0.5)):
            team_logo_path = f"/path/to/{team_tag}.svg.png"
            if os.path.exists(team_logo_path):
                team_logo = Image.open(team_logo_path)
                team_logo_resized = resize_image_to_bounding_box(team_logo, target_width=30, target_height=30)
                logo = OffsetImage(np.array(team_logo_resized), zoom=1)
                ab = AnnotationBbox(logo, (x, y), frameon=False, box_alignment=box_alignment)
                ax.add_artist(ab)
        
    # Replace y-axis labels with logos
    for i, team_tag in enumerate(kreuztabelle.index):
            add_logo_at_position(ax, team_tag, -1, i)
        
    # Replace x-axis labels with logos
    for j, team_tag in enumerate(kreuztabelle.columns):
            add_logo_at_position(ax, team_tag, j, -1, box_alignment=(0.5, 0.5))  # Place logos at the bottom of the grid
        
    # Remove the default x and y labels
    ax.set_xticks([])
    ax.set_yticks([])
        
    # Display the chart
    st.pyplot(fig)