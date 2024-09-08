import streamlit as st
from PIL import Image
import numpy as np
from bundesliga.utils import resize_logo, load_image  # Ensure resize_logo is imported

def display_form_guide_section(df, selected_season, selected_matchday, selected_match, df_matches):
    if selected_season != '--' and selected_matchday != '--' and selected_match != '--':
        selected_match_row = df_matches[
            df_matches.apply(lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1) == selected_match
        ]

        # Add a check to avoid out-of-bounds errors
        if selected_match_row.empty:
            st.error(f"No match found for the selected match: {selected_match}")
            return
        
        selected_match_row = selected_match_row.iloc[0]

        home_team_tag = selected_match_row['Home Tag']
        away_team_tag = selected_match_row['Away Tag']
        matchday = selected_match_row['Matchday']

        # Display the Form Guide for both teams
        st.subheader("Form Guide")

        col1, col_space, col2 = st.columns([4, 1, 4])

        with col1:
            home_team_matches = df[(df['Season'] == selected_season) & ((df['Home Tag'] == home_team_tag) | (df['Away Tag'] == home_team_tag))]
            last_n_home_matches = min(len(home_team_matches[home_team_matches['Matchday'] < matchday]), 5)
            
            # Update the header based on the season
            if selected_season == '2023/24':
                header_text = f"{home_team_tag} Last {last_n_home_matches} Match{'es' if last_n_home_matches > 1 else ''}"
            else:
                header_text = f"{home_team_tag} Previous {last_n_home_matches} Match{'es' if last_n_home_matches > 1 else ''}"
            
            st.markdown(f"<h4 style='text-align: left;'>{header_text}</h4>", unsafe_allow_html=True)
            display_form_guide(home_team_matches, home_team_tag, matchday)

        with col2:
            away_team_matches = df[(df['Season'] == selected_season) & ((df['Home Tag'] == away_team_tag) | (df['Away Tag'] == away_team_tag))]
            last_n_away_matches = min(len(away_team_matches[away_team_matches['Matchday'] < matchday]), 5)
            
            # Update the header based on the season
            if selected_season == '2023/24':
                header_text = f"{away_team_tag} Last {last_n_away_matches} Match{'es' if last_n_away_matches > 1 else ''}"
            else:
                header_text = f"{away_team_tag} Previous {last_n_away_matches} Match{'es' if last_n_away_matches > 1 else ''}"
            
            st.markdown(f"<h4 style='text-align: left;'>{header_text}</h4>", unsafe_allow_html=True)
            display_form_guide(away_team_matches, away_team_tag, matchday)

def display_form_guide(df_season, team_tag, matchday):
    # Filter the matches for the last 5 games
    last_5_matches = df_season[((df_season['Home Tag'] == team_tag) | (df_season['Away Tag'] == team_tag)) & 
                               (df_season['Matchday'] < matchday)].tail(5)

    # Reverse the order to show the most recent match first
    last_5_matches = last_5_matches.iloc[::-1]

    # Display last 5 matches as squares or rectangles with logos
    cols = st.columns(5)
    for i, (index, match) in enumerate(last_5_matches.iterrows()):
        # Determine if the team being analyzed was the home or away team in this match
        is_home_team = match['Home Tag'] == team_tag

        # Get the correct score format with home goals on the left and away goals on the right
        if is_home_team:
            score = f"{match['Home Goals']} - {match['Away Goals']}"
        else:
            score = f"{match['Home Goals']} - {match['Away Goals']}"

        # Determine the result from the team's perspective
        team_goals = match['Home Goals'] if is_home_team else match['Away Goals']
        opponent_goals = match['Away Goals'] if is_home_team else match['Home Goals']
        if team_goals > opponent_goals:
            result = 'W'  # Win
        elif team_goals < opponent_goals:
            result = 'L'  # Loss
        else:
            result = 'T'  # Tie

        # Set color based on the result from the perspective of the team_tag
        color, border_color = get_result_color(result)

        # Load and resize the logos
        home_logo_resized, away_logo_resized = get_resized_logos(match['Home Tag'], match['Away Tag'])

        # Create the panel layout
        with cols[i]:
            # Place logos according to home/away status
            st.markdown(
                f"<div style='background-color:{color}; padding:5px; text-align:center; border-radius:5px; border: 2px solid {border_color};'>"
                f"<div style='display: flex; justify-content: center; align-items: center;'>"
                f"<div style='padding-right: 3px;'><img src='data:image/png;base64,{image_to_base64(home_logo_resized)}' style='height:auto; width:50px;' /></div>"
                f"<div style='padding-left: 3px;'><img src='data:image/png;base64,{image_to_base64(away_logo_resized)}' style='height:auto; width:50px;' /></div>"
                f"</div>"
                f"<div style='margin-top:5px; font-size:14px; background-color:rgb(14, 17, 23); color:white; border-radius:12px; padding:3px; border: 1px solid {border_color};'>{score}</div>"
                f"</div>", 
                unsafe_allow_html=True
            )

def get_result_and_score(team_goals, opponent_goals):
    """Helper function to determine the result (W, L, T) and format the score."""
    if team_goals > opponent_goals:
        return 'W', f"{team_goals} - {opponent_goals}"
    elif team_goals < opponent_goals:
        return 'L', f"{team_goals} - {opponent_goals}"
    else:
        return 'T', f"{team_goals} - {opponent_goals}"

def get_result_color(result):
    """Helper function to get color based on match result."""
    if result == 'W':
        return '#a8e6a1', '#388e3c'  # Darker Green for win
    elif result == 'L':
        return '#ff9999', '#c62828'  # Darker Red for loss
    else:
        return '#c4c4c4', '#696969'  # Darker Grey for tie

def get_resized_logos(home_tag, away_tag):
    """Helper function to load and resize team logos."""
    home_logo_path = f"data/logos/team_logos/{home_tag}.svg.png"
    away_logo_path = f"data/logos/team_logos/{away_tag}.svg.png"
    
    home_logo = load_image(home_logo_path)
    away_logo = load_image(away_logo_path)
    
    home_logo_resized = resize_logo(home_logo, max_width=50)
    away_logo_resized = resize_logo(away_logo, max_width=50)

    return home_logo_resized, away_logo_resized

def image_to_base64(image):
    """Helper function to convert image to base64 for HTML display."""
    import base64
    from io import BytesIO
    
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str