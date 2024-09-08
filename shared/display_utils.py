import streamlit as st
from PIL import Image
import base64
from io import BytesIO

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

def resize_image(image, target_area):
    # Logic to resize images
    width, height = image.size
    aspect_ratio = height / width
    new_width = int((target_area / aspect_ratio) ** 0.5)
    new_height = int(aspect_ratio * new_width)
    return image.resize((new_width, new_height))

def load_image(image_path):
    # Logic to load an image from a given path
    try:
        return Image.open(image_path)
    except FileNotFoundError:
        st.error(f"Image at {image_path} not found.")
        return None

def image_to_bytes(image):
    # Utility function to convert an image to bytes (used for displaying images)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str