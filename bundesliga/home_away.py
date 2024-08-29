import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from PIL import Image
from io import BytesIO
import base64
from bundesliga.utils import get_team_colors, resize_image_to_bounding_box, image_to_base64

# Function to filter matches based on the selected season and matchday
def filter_home_away_matches(df, selected_season, matchday):
    if selected_season == '2023/24':
        # Exclude data from the selected matchday for 2023/24 season (preview mode)
        return df[(df['Season'] == selected_season) & (df['Matchday'] < matchday)]
    else:
        # Include data from the selected matchday for 2005/06 to 2022/23 seasons
        return df[(df['Season'] == selected_season) & (df['Matchday'] <= matchday)]

# Function to calculate points for each team when they were playing at home or away
def calculate_home_away_points(df_filtered, home_away):
    points_data = []

    for index, row in df_filtered.iterrows():
        if home_away == 'home':
            team_tag = row['Home Tag']
            if row['Result'] == 'Home Win':
                points = 3
            elif row['Result'] == 'Tie':
                points = 1
            else:
                points = 0
        elif home_away == 'away':
            team_tag = row['Away Tag']
            if row['Result'] == 'Away Win':
                points = 3
            elif row['Result'] == 'Tie':
                points = 1
            else:
                points = 0
        
        points_data.append((team_tag, points))
    
    # Create a DataFrame and aggregate points by team
    df_points = pd.DataFrame(points_data, columns=['Team Tag', 'Points'])
    df_points = df_points.groupby('Team Tag')['Points'].sum().reset_index()

    return df_points.sort_values(by='Points', ascending=False)

# Function to plot the league table for home or away records
def plot_home_away_table(df_points, title, color_codes_df, home_away):
    if df_points.empty:
        return None  # If the points DataFrame is empty, exit early
    
    fig = go.Figure()

    for i, (team_tag, points) in enumerate(zip(df_points['Team Tag'], df_points['Points'])):
        primary_color, secondary_color = get_team_colors(team_tag, color_codes_df)

        # Add the bar for the team with a white outline
        fig.add_trace(go.Bar(
            y=[i + 1],
            x=[points],
            orientation='h',
            marker=dict(
                color=primary_color,
                line=dict(color='white', width=0.5)  # Add white outlines with 0.5px width
            ),
            name=team_tag,
            showlegend=False
        ))

        # Load and resize team logo
        logo_path = f"data/logos/team_logos/{team_tag}.svg.png"
        try:
            team_logo = Image.open(logo_path)
        except FileNotFoundError:
            continue
        
        team_logo_resized = resize_image_to_bounding_box(team_logo, target_width=40, target_height=40)
        logo_base64 = image_to_base64(team_logo_resized)

        # Position the logo to the right of the bar
        fig.add_layout_image(
            dict(
                source=f'data:image/png;base64,{logo_base64}',
                xref="x", yref="y",
                x=points + 1,
                y=i + 1,
                sizex=7,
                sizey=0.6,
                xanchor="left",
                yanchor="middle",
                layer="above"
            )
        )

    # Update the x-axis range to 0-50
    fig.update_layout(
        title=title,
        xaxis=dict(title='Points', showgrid=False, zeroline=False, range=[0, 50]),
        yaxis=dict(showgrid=False, zeroline=False, tickvals=list(range(1, 19)), ticktext=list(range(1, 19)), autorange="reversed"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=80, b=40),
        height=800,
        width=1000
    )

    return fig

# Utility functions for resizing images and converting to base64
def resize_image(image, max_width, max_height=None):
    width, height = image.size
    aspect_ratio = width / height

    if max_height:
        target_height = min(height, max_height)
        target_width = int(target_height * aspect_ratio)
    else:
        target_width = max_width
        target_height = int(target_width / aspect_ratio)

    return image.resize((target_width, target_height), Image.LANCZOS)

def image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# Function to display the home/away tables
def display_home_away_tables(df, selected_season, matchday, color_codes_df):
    # Ensure the correct filtering of matchdays and the proper display of matchday in the title
    df_filtered = filter_home_away_matches(df, selected_season, matchday)
    
    # Adjust the matchday for display if the selected season is 2023/24
    if selected_season == '2023/24':
        matchday_display = matchday - 1
    else:
        matchday_display = matchday

    # Adjust the matchday for display if the selected season is 2023/24
    if selected_season == '2023/24':
        matchday_display = matchday - 1
    else:
        matchday_display = matchday

    # Display Home Table
    st.subheader(f"Home Table After Matchday {matchday_display} ({selected_season})")
    df_home_points = calculate_home_away_points(df_filtered, home_away='home')
    home_fig = plot_home_away_table(df_home_points, f'Home Table After Matchday {matchday_display} ({selected_season})', color_codes_df, home_away='home')
    st.plotly_chart(home_fig, use_container_width=True)

    # Display Away Table
    st.subheader(f"Away Table After Matchday {matchday_display} ({selected_season})")
    df_away_points = calculate_home_away_points(df_filtered, home_away='away')
    away_fig = plot_home_away_table(df_away_points, f'Away Table After Matchday {matchday_display} ({selected_season})', color_codes_df, home_away='away')
    st.plotly_chart(away_fig, use_container_width=True)
        
    
