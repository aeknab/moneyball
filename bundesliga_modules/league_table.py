import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
from io import BytesIO
import base64
from bundesliga.cross_table import display_cross_table_view  # Import the cross table function
from bundesliga.utils import get_team_colors, resize_image, image_to_base64

# Function to resize images
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

# Function to convert image to base64 for Plotly
def image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# Function to filter matches before the selected matchday
def filter_matches_before(df, selected_season, matchday):
    return df[(df['Season'] == selected_season) & (df['Matchday'] < matchday)]

# Function to calculate team points
def calculate_team_points(df_filtered):
    points_data = []

    for index, row in df_filtered.iterrows():
        points_data.append((row['Home Tag'], row['Home Team Points']))
        points_data.append((row['Away Tag'], row['Away Team Points']))

    df_points = pd.DataFrame(points_data, columns=['Team Tag', 'Points']).groupby('Team Tag').max().reset_index()

    return df_points.sort_values(by='Points', ascending=False)

# Function to plot the static league table with team logos
def plot_league_table(df_points, title, color_codes_df):
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
            showlegend=False  # Hide the legend for each bar
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

    fig.update_layout(
        title=title,
        xaxis=dict(title='Points', showgrid=False, zeroline=False, range=[0, 100]),
        yaxis=dict(showgrid=False, zeroline=False, tickvals=list(range(1, 19)), ticktext=list(range(1, 19)), autorange="reversed"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=80, b=40),
        height=800,
        width=1000
    )

    st.plotly_chart(fig, use_container_width=True)

# Function to get the points of each team at the end of each matchday for animation
def get_team_points_per_matchday(df_filtered):
    home_points = df_filtered[['Matchday', 'Home Tag', 'Home Team Points']].rename(
        columns={'Home Tag': 'Team Tag', 'Home Team Points': 'Points'}
    )
    away_points = df_filtered[['Matchday', 'Away Tag', 'Away Team Points']].rename(
        columns={'Away Tag': 'Team Tag', 'Away Team Points': 'Points'}
    )

    df_points = pd.concat([home_points, away_points]).drop_duplicates().sort_values(by=['Matchday', 'Points'], ascending=[True, False])
    df_points['Rank'] = df_points.groupby('Matchday')['Points'].rank(method='first', ascending=False)
    
    return df_points

# Function to create the animated league table with logos
def create_league_table_animation(df_points, color_codes_df):
    # Merge with color data
    df_points = df_points.merge(color_codes_df[['Tag', 'Primary', 'Secondary']], how='left', left_on='Team Tag', right_on='Tag')

    # Create the bar chart animation with Plotly Express
    fig = px.bar(df_points,
                 x='Points',
                 y='Rank',
                 color='Team Tag',
                 orientation='h',
                 animation_frame='Matchday',
                 range_x=[0, 100],
                 range_y=[0.5, 18.5],
                 color_discrete_map={team: color for team, color in zip(color_codes_df['Tag'], color_codes_df['Primary'])})

    # Customize the layout
    fig.update_layout(
        yaxis=dict(autorange="reversed", title='Rank', tickvals=list(range(1, 19))),
        xaxis=dict(title='Points', range=[0, 100]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=800,
        width=1000,
    )

    # Overlaying logos using Plotly graph_objects
    frames = []
    unique_matchdays = df_points['Matchday'].unique()

    for matchday in unique_matchdays:
        df_day = df_points[df_points['Matchday'] == matchday]
        layout_images_frame = []

        for _, row in df_day.iterrows():
            logo_path = f"data/logos/team_logos/{row['Team Tag']}.svg.png"
            team_logo = Image.open(logo_path)
            team_logo_resized = resize_image(team_logo, 40)
            logo_base64 = image_to_base64(team_logo_resized)

            layout_images_frame.append(
                dict(
                    source=f'data:image/png;base64,{logo_base64}',
                    xref="x",
                    yref="y",
                    x=row['Points'] + 2,  # Position slightly to the right of the bar
                    y=row['Rank'],
                    sizex=5,  # Adjust size to match bar height
                    sizey=0.7,
                    xanchor="left",
                    yanchor="middle",
                    layer="above"
                )
            )

        # Combine the express data with graph_objects for each frame
        frames.append(go.Frame(data=fig.data, layout=dict(images=layout_images_frame), name=str(matchday)))

    # Update the figure with frames
    fig_go = go.Figure(fig)
    fig_go.frames = frames

    # Add animation controls
    fig_go.update_layout(updatemenus=[dict(type="buttons",
                                           buttons=[dict(label="Play",
                                                         method="animate",
                                                         args=[None, {"frame": {"duration": 500, "redraw": True},
                                                                      "fromcurrent": True,
                                                                      "mode": "immediate"}]),
                                                    dict(label="Pause",
                                                         method="animate",
                                                         args=[[None], {"frame": {"duration": 0, "redraw": False},
                                                                        "mode": "immediate"}])])])

    st.plotly_chart(fig_go, use_container_width=True)

# Function to display the league tables with animation and cross table
def display_league_tables(df, selected_season, matchday, view_selection, color_codes_df):
    st.header("League Table")

    # Create four buttons in four columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Full Season Table"):
            view_selection = "Full Table"
    with col2:
        if st.button("Home/Away Table"):
            view_selection = "Home/Away"
    with col3:
        if st.button("1st/2nd Leg Table"):
            view_selection = "1st/2nd Leg"
    with col4:
        if st.button("Cross Table"):
            view_selection = "Cross Table"

    df_filtered = filter_matches_before(df, selected_season, matchday)

    if view_selection == "Full Table":
        df_points = calculate_team_points(df_filtered)
        plot_league_table(df_points, f'Bundesliga League Table After Matchday {matchday - 1} ({selected_season})', color_codes_df)

    elif view_selection == "Cross Table":
        display_cross_table_view(df, selected_season, matchday)

    # Sub-header for animation
    st.subheader("Play Animation")
    if st.button("Play Animation"):
        df_points = get_team_points_per_matchday(df_filtered)
        create_league_table_animation(df_points, color_codes_df)
