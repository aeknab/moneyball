import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from io import BytesIO
import base64
from bundesliga.utils import get_team_colors, resize_image, image_to_base64

# Function to filter matches based on the selected season and leg (1st or 2nd) and matchday
def filter_leg_matches(df, selected_season, leg, matchday):
    if leg == '1st':
        return df[(df['Season'] == selected_season) & (df['Matchday'] < matchday) & (df['Matchday'] <= 17)]
    elif leg == '2nd':
        if matchday < 18:
            return pd.DataFrame()  # Return empty DataFrame if matchday is before the 2nd leg starts
        return df[(df['Season'] == selected_season) & (df['Matchday'] < matchday) & (df['Matchday'] >= 18)]

# Function to calculate points for each team in either the 1st or 2nd leg
def calculate_leg_points(df_filtered):
    if df_filtered.empty:
        return pd.DataFrame(columns=['Team Tag', 'Points'])  # Return an empty DataFrame if no data is available

    points_data = []

    for index, row in df_filtered.iterrows():
        # Calculate points for both home and away teams
        if row['Result'] == 'Home Win':
            points_data.append((row['Home Tag'], 3))
            points_data.append((row['Away Tag'], 0))
        elif row['Result'] == 'Away Win':
            points_data.append((row['Home Tag'], 0))
            points_data.append((row['Away Tag'], 3))
        elif row['Result'] == 'Tie':
            points_data.append((row['Home Tag'], 1))
            points_data.append((row['Away Tag'], 1))

    # Create a DataFrame and aggregate points by team
    df_points = pd.DataFrame(points_data, columns=['Team Tag', 'Points'])
    df_points = df_points.groupby('Team Tag')['Points'].sum().reset_index()

    return df_points.sort_values(by='Points', ascending=False)

# Function to plot the league table for either the 1st or 2nd leg
def plot_leg_table(df_points, title, color_codes_df):
    if df_points.empty:
        return None  # Return None if there's no data to plot

    fig = go.Figure()

    for i, (team_tag, points) in enumerate(zip(df_points['Team Tag'], df_points['Points'])):
        primary_color, secondary_color = get_team_colors(team_tag, color_codes_df)

        # Add the bar for the team
        fig.add_trace(go.Bar(
            y=[i + 1],
            x=[points],
            orientation='h',
            marker=dict(color=primary_color),
            name=team_tag,
            showlegend=False
        ))

        # Load and resize team logo
        logo_path = f"data/logos/team_logos/{team_tag}.svg.png"
        team_logo = Image.open(logo_path)
        team_logo_resized = resize_image(team_logo, 40)
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

    # Update the x-axis range to 0-50 (as requested earlier)
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
