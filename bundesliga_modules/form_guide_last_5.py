import streamlit as st
from PIL import Image
import numpy as np
from bundesliga.utils import resize_logo, load_image  # Ensure resize_logo is imported

def display_form_guide_section(df, selected_season, selected_matchday, selected_match, df_matches):
    if selected_season != '--' and selected_matchday != '--' and selected_match != '--':
        selected_match_row = df_matches[
            df_matches.apply(lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1) == selected_match
        ].iloc[0]

        home_team_tag = selected_match_row['Home Tag']
        away_team_tag = selected_match_row['Away Tag']
        matchday = selected_match_row['Matchday']

        # Display the Form Guide for both teams
        st.subheader("Form Guide")

        col1, col_space, col2 = st.columns([4, 1, 4])

        with col1:
            st.markdown(f"<h4 style='text-align: left;'>{home_team_tag} Last 5 Matches</h4>", unsafe_allow_html=True)
            display_form_guide(df[df['Season'] == selected_season], home_team_tag, matchday)

        with col2:
            st.markdown(f"<h4 style='text-align: left;'>{away_team_tag} Last 5 Matches</h4>", unsafe_allow_html=True)
            display_form_guide(df[df['Season'] == selected_season], away_team_tag, matchday)


def display_form_guide(df_season, team_tag, matchday):
    # Filter the matches for the last 5 games
    last_5_matches = df_season[((df_season['Home Tag'] == team_tag) | (df_season['Away Tag'] == team_tag)) & 
                               (df_season['Matchday'] < matchday)].tail(5)

    # Function to get the match result
    def get_match_result(match, team_tag):
        if match['Home Tag'] == team_tag:
            if match['Home Goals'] > match['Away Goals']:
                return 'W', f"{match['Home Goals']} - {match['Away Goals']}", match['Home Tag'], match['Away Tag'], True
            elif match['Home Goals'] < match['Away Goals']:
                return 'L', f"{match['Home Goals']} - {match['Away Goals']}", match['Home Tag'], match['Away Tag'], True
            else:
                return 'T', f"{match['Home Goals']} - {match['Away Goals']}", match['Home Tag'], match['Away Tag'], True
        else:
            if match['Away Goals'] > match['Home Goals']:
                return 'W', f"{match['Away Goals']} - {match['Home Goals']}", match['Away Tag'], match['Home Tag'], False
            elif match['Away Goals'] < match['Home Goals']:
                return 'L', f"{match['Away Goals']} - {match['Home Goals']}", match['Away Tag'], match['Home Tag'], False
            else:
                return 'T', f"{match['Away Goals']} - {match['Home Goals']}", match['Away Tag'], match['Home Tag'], False

    # Reverse the order to show the most recent match first
    last_5_matches = last_5_matches.iloc[::-1]

    # Display last 5 matches as squares or rectangles with logos
    cols = st.columns(5)
    for i, (index, match) in enumerate(last_5_matches.iterrows()):
        result, score, home_tag, away_tag, is_home = get_match_result(match, team_tag)
        if result == 'W':
            color = '#a8e6a1'  # Darker Green
            border_color = '#556B2F'  # Even Darker Green for border
        elif result == 'L':
            color = '#ff9999'  # Darker Red
            border_color = '#8B0000'  # Even Darker Red for border
        else:
            color = '#c4c4c4'  # Darker Grey
            border_color = '#696969'  # Even Darker Grey for border

        # Load and resize the logos
        home_logo_resized, away_logo_resized = get_resized_logos(home_tag, away_tag)

        # Create the panel layout
        with cols[i]:
            if is_home:
                logos_html = (
                    f"<div style='padding-right: 3px;'><img src='data:image/png;base64,{image_to_base64(home_logo_resized)}' style='height:auto; width:50px;' /></div>"
                    f"<div style='padding-left: 3px;'><img src='data:image/png;base64,{image_to_base64(away_logo_resized)}' style='height:auto; width:50px;' /></div>"
                )
            else:
                logos_html = (
                    f"<div style='padding-right: 3px;'><img src='data:image/png;base64,{image_to_base64(away_logo_resized)}' style='height:auto; width:50px;' /></div>"
                    f"<div style='padding-left: 3px;'><img src='data:image/png;base64,{image_to_base64(home_logo_resized)}' style='height:auto; width:50px;' /></div>"
                )

            st.markdown(
                f"<div style='background-color:{color}; padding:5px; text-align:center; border-radius:5px; border: 2px solid {border_color};'>"
                f"<div style='display: flex; justify-content: center; align-items: center;'>{logos_html}</div>"
                f"<div style='margin-top:5px; font-size:14px; background-color:rgb(14, 17, 23); color:white; border-radius:12px; padding:3px; border: 1px solid {border_color};'>{score}</div>"
                f"</div>", 
                unsafe_allow_html=True
            )

def get_resized_logos(home_tag, away_tag):
    home_logo_path = f"data/logos/team_logos/{home_tag}.svg.png"
    away_logo_path = f"data/logos/team_logos/{away_tag}.svg.png"
    
    home_logo = load_image(home_logo_path)
    away_logo = load_image(away_logo_path)
    
    # Resizing images for consistent size based on width and maintaining aspect ratio
    home_logo_resized = resize_logo(home_logo, max_width=50)
    away_logo_resized = resize_logo(away_logo, max_width=50)

    return home_logo_resized, away_logo_resized


def image_to_base64(image):
    import base64
    from io import BytesIO
    
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str