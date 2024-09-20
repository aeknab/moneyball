# table_display.py

import streamlit as st
from PIL import Image
import base64
from bundesliga.utils import load_image

def image_to_bytes(image):
    from io import BytesIO
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str

def display_styled_team_table(home_data, away_data):
    def get_team_logo_img_tag(team_tag):
        """Return an HTML image tag for the team logo."""
        logo_path = f"data/logos/team_logos/{team_tag}.svg.png"
        logo_image = load_image(logo_path)
        logo_img_tag = f'<img src="data:image/png;base64,{image_to_bytes(logo_image)}" style="max-width: 20px; max-height: 20px; vertical-align: middle;" />'
        return logo_img_tag

    # Sort the teams by rank, ensuring that the higher-ranked team is on top
    teams_data = [home_data, away_data]
    teams_data_sorted = sorted(teams_data, key=lambda x: int(x['rank']) if x['rank'] != '--' else float('inf'))

    # Generating HTML image tags for the home and away team logos after sorting
    team1 = teams_data_sorted[0]
    team2 = teams_data_sorted[1]
    
    team1_logo_tag = get_team_logo_img_tag(team1['team_tag'])
    team2_logo_tag = get_team_logo_img_tag(team2['team_tag'])

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

    # Display sorted teams
    st.markdown(
        f"""
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>↕️</th>
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
                    <td>{team1['rank']}</td>
                    <td>{team1['movement']}</td>
                    <td>{team1_logo_tag} {team1['team_tag']}</td>
                    <td>{team1['games']}</td>
                    <td>{team1['wins']}</td>
                    <td>{team1['ties']}</td>
                    <td>{team1['losses']}</td>
                    <td>{team1['goals_scored']} : {team1['goals_conceded']}</td>
                    <td>{team1['gd']}</td>
                    <td><b>{team1['points']}</b></td>
                </tr>
                <tr>
                    <td>{team2['rank']}</td>
                    <td>{team2['movement']}</td>
                    <td>{team2_logo_tag} {team2['team_tag']}</td>
                    <td>{team2['games']}</td>
                    <td>{team2['wins']}</td>
                    <td>{team2['ties']}</td>
                    <td>{team2['losses']}</td>
                    <td>{team2['goals_scored']} : {team2['goals_conceded']}</td>
                    <td>{team2['gd']}</td>
                    <td><b>{team2['points']}</b></td>
                </tr>
            </tbody>
        </table>
        """,
        unsafe_allow_html=True
    )