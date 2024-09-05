import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
from io import BytesIO
import base64

# Function to display the group table as a static chart
def display_group_table(matchday, rankings_df, selected_player):
    st.subheader("Group Table")

    # Filter rankings data up to and including the selected matchday
    filtered_rankings_df = rankings_df[rankings_df['Spieltag'] == matchday]

    # Calculate the total points for each player for the current matchday
    player_points = filtered_rankings_df.groupby('Name')['Gesamtpunkte'].sum()

    # Sort the players by their total points
    player_points = player_points.sort_values(ascending=False)

    # Determine bar colors based on the selected player
    if selected_player == 'All':
        bar_colors = [color_palette.get(player, 'rgba(179, 179, 179, 0.75)') for player in player_points.index]
    else:
        bar_colors = [color_palette.get("Gray") if player != selected_player else color_palette.get(selected_player, 'rgba(179, 179, 179, 0.75)') for player in player_points.index]

    # Create a Plotly figure
    fig = go.Figure()

    # Add a bar for each player with their specific color
    for player, color in zip(player_points.index, bar_colors):
        fig.add_trace(go.Bar(
            x=[player_points[player]],
            y=[player],
            orientation='h',
            name=player,
            marker=dict(color=color)
        ))

    # Set layout
    fig.update_layout(
        title_text=f'Group League Table - Matchday {matchday}',
        xaxis_title='Points',
        yaxis=dict(autorange='reversed'),  
        template='plotly_white',
        height=400,
        margin=dict(l=100, r=20, t=50, b=50)
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Define the new ColorBrewer Set2 color palette for players with 85% transparency
color_palette = {
    "Andreas": "rgba(102, 194, 165, 0.85)",  # light green
    "Gerd": "rgba(252, 141, 98, 0.85)",      # light orange
    "Geri": "rgba(141, 160, 203, 0.85)",     # light blue
    "Hermann": "rgba(231, 138, 195, 0.85)",  # light pink
    "Johnny": "rgba(166, 216, 84, 0.85)",    # light lime green
    "Moddy": "rgba(255, 217, 47, 0.85)",     # light yellow
    "Samson": "rgba(229, 196, 148, 0.85)",   # light brown
    "Gray": "rgba(179, 179, 179, 0.50)"      # light gray for other players when a single player is selected
}

# Utility function to convert an image to base64 for Plotly
def image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str

# Function to calculate player points for each matchday and their ranks
def get_player_points_per_matchday(rankings_df):
    # No need to accumulate, just use 'Gesamtpunkte' for rankings
    player_points_per_day = rankings_df[['Spieltag', 'Name', 'Gesamtpunkte']]

    # Rank players based on total points ('Gesamtpunkte')
    player_points_per_day['Rank'] = player_points_per_day.groupby('Spieltag')['Gesamtpunkte'].rank(method='first', ascending=False)

    return player_points_per_day

# Function to create the animated group table with logos, handling ties in points
def create_group_table_animation(player_points_long, selected_players):
    # Ensure all matchdays up to 34 are included in the animation frames
    player_points_long['Spieltag'] = player_points_long['Spieltag'].astype(int)
    matchdays = list(range(1, 35))  # Explicitly define matchdays from 1 to 34

    # Create a complete DataFrame to ensure every player has data for every matchday
    all_players = player_points_long['Name'].unique()
    complete_index = pd.MultiIndex.from_product([matchdays, all_players], names=['Spieltag', 'Name'])
    player_points_long = player_points_long.set_index(['Spieltag', 'Name']).reindex(complete_index, fill_value=0).reset_index()

    # Rank players by total points ('Gesamtpunkte') for each matchday
    player_points_long['Rank'] = player_points_long.groupby('Spieltag')['Gesamtpunkte'].rank(method='first', ascending=False)

    # Initialize the figure
    fig = go.Figure()

    # Create initial bars and logos for the first matchday
    matchday = 1
    df_day = player_points_long[player_points_long['Spieltag'] == matchday]

    for i, row in df_day.iterrows():
        player = row['Name']
        points = row['Gesamtpunkte']
        rank = row['Rank']

        # Determine color based on whether the player is selected or not
        primary_color = color_palette.get(player, 'rgba(179, 179, 179, 0.75)')

        # Add bars
        fig.add_trace(go.Bar(
            x=[points],
            y=[rank],
            orientation='h',
            marker=dict(
                color=primary_color,
                line=dict(color='white', width=0.5)  # White outlines with reduced width
            ),
            name=player,
            showlegend=False
        ))

    # Update layout
    fig.update_layout(
        yaxis=dict(autorange="reversed", title='Rank', tickvals=list(range(1, len(all_players) + 1))),
        xaxis=dict(title='Points', range=[0, player_points_long['Gesamtpunkte'].max() + 50]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=600,
        width=800
    )

    # Add player logos for the first frame
    layout_images = []
    for _, row in df_day.iterrows():
        player = row['Name']
        rank = row['Rank']
        points = row['Gesamtpunkte']

        player_logo_path = f"data/logos/groups/{player}.png"
        player_logo = Image.open(player_logo_path)
        player_logo_resized = player_logo.resize((40, 40))
        logo_base64 = image_to_base64(player_logo_resized)

        layout_images.append(
            dict(
                source=f'data:image/png;base64,{logo_base64}',
                xref="x", yref="y",
                x=points + 1,
                y=rank,
                sizex=25,
                sizey=3.5,
                xanchor="left",
                yanchor="middle",
                layer="above"
            )
        )

    fig.update_layout(images=layout_images)

    # Generate frames for each matchday
    frames = []
    for matchday in matchdays:
        df_day = player_points_long[player_points_long['Spieltag'] == matchday]
        frame_data = []
        layout_images_frame = []

        for i, row in df_day.iterrows():
            player = row['Name']
            points = row['Gesamtpunkte']
            rank = row['Rank']

            # Update bars instead of replacing them
            frame_data.append(go.Bar(
                x=[points],
                y=[rank],
                orientation='h',
                marker=dict(
                    color=color_palette.get(player, 'rgba(179, 179, 179, 0.75)'),
                    line=dict(color='white', width=0.5)
                ),
                name=player,
                showlegend=False
            ))

            # Add logo image update for the frame
            player_logo_path = f"data/logos/groups/{player}.png"
            player_logo = Image.open(player_logo_path)
            player_logo_resized = player_logo.resize((40, 40))
            logo_base64 = image_to_base64(player_logo_resized)

            layout_images_frame.append(
                dict(
                    source=f'data:image/png;base64,{logo_base64}',
                    xref="x",
                    yref="y",
                    x=points + 1,
                    y=rank,
                    sizex=25,
                    sizey=3.5,
                    xanchor="left",
                    yanchor="middle",
                    layer="above"
                )
            )

        frames.append(go.Frame(data=frame_data, layout=dict(images=layout_images_frame), name=str(matchday)))

    # Add frames to the figure
    fig.frames = frames

    # Move the buttons to the left and the slider to the right
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                x=0.05,  # Position on the left
                y=-0.1,  # Position below the chart
                showactive=True,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True, "mode": "immediate"}]
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]
                    )
                ]
            )
        ],
        sliders=[{
            "steps": [{"args": [[str(i)], {"frame": {"duration": 500, "redraw": True}, "mode": "immediate"}], "label": str(i), "method": "animate"} for i in matchdays],
            "currentvalue": {"prefix": "Matchday: "},
            "xanchor": "right",
            "x": 0.55,
            "len": 0.4,
            "pad": {"b": 10},
        }]
    )

    st.plotly_chart(fig, use_container_width=True)