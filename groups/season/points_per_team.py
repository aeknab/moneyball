import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from groups.utils import get_team_colors, image_to_base64, calculate_points

# Function to tally points per team
def calculate_points_per_team(df, selected_players, matchday):
    # Filter data for the selected matchday or up to the selected matchday
    df_filtered = df[df['Matchday'] <= matchday]

    # Initialize a dictionary to store points per team
    points_per_team = {}

    for _, row in df_filtered.iterrows():
        home_team = row['Home Team']
        away_team = row['Away Team']
        home_goals_actual = row['Home Goals']
        away_goals_actual = row['Away Goals']

        # Skip the row if the actual goals are missing
        if pd.isna(home_goals_actual) or pd.isna(away_goals_actual):
            continue

        for player in selected_players:
            home_goals_pred = row[f'{player} Home Goals Predicted']
            away_goals_pred = row[f'{player} Away Goals Predicted']

            # Skip if the prediction is missing
            if pd.isna(home_goals_pred) or pd.isna(away_goals_pred):
                continue

            # Calculate the points for the player in this match
            player_points = calculate_points(home_goals_pred, away_goals_pred, home_goals_actual, away_goals_actual)

            # Add the points to both teams (since the match involves both teams)
            points_per_team[home_team] = points_per_team.get(home_team, 0) + player_points
            points_per_team[away_team] = points_per_team.get(away_team, 0) + player_points

    # Convert the dictionary to a DataFrame and sort by points
    df_points = pd.DataFrame(list(points_per_team.items()), columns=['Team', 'Points']).sort_values(by='Points', ascending=False)

    return df_points

# Function to display the vertical bar chart of points per team
def display_points_per_team_bar_chart(df, selected_players, matchday, color_codes_df):
    # Calculate points per team
    points_per_team = calculate_points_per_team(df, selected_players, matchday)

    # Calculate the average points across all teams
    average_points = points_per_team['Points'].mean()

    # Determine if "All players" is selected
    is_all_players = len(selected_players) > 1

    # Initialize the Plotly figure
    fig = go.Figure()

    # Define the scaling factor for logo sizes and y-offset for the logos
    scale_factor = 7 if is_all_players else 1
    y_offset = 5 if is_all_players else 1  # Reduce y-offset to half (from 10 to 5)

    for i, (team, points) in enumerate(zip(points_per_team['Team'], points_per_team['Points'])):
        primary_color, secondary_color = get_team_colors(team, color_codes_df)

        # Add a bar for the team
        fig.add_trace(go.Bar(
            x=[team],
            y=[points],
            marker=dict(color=primary_color),
            showlegend=False
        ))

        # Calculate the deviation from the average
        deviation = round(points - average_points, 1)

        # Determine the position to display the deviation label
        deviation_y = average_points + (3 if deviation >= 0 else -3)

        # Add a label for the deviation from the average in the secondary color
        fig.add_annotation(
            x=team,
            y=0.1 * points,  # Position inside the bar at 10% of the bar height
            text=f"{'+' if deviation > 0 else ''}{deviation}",  # Positive/Negative label
            showarrow=False,
            font=dict(color=secondary_color, size=12),
            xanchor='center',
            yanchor='bottom',  # Position the text inside the bar
            textangle=0  # Keep the text horizontal
        )

        # Load the team logo
        logo_path = f"data/logos/team_logos/{team}.svg.png"
        team_logo = Image.open(logo_path)

        # Calculate the aspect ratio of the logo
        aspect_ratio = team_logo.width / team_logo.height

        # Set the size parameters based on the aspect ratio and the scale factor
        if aspect_ratio > 1:
            # Logo is wider than it is tall
            sizex = 3 * scale_factor  # Adjust width with scaling factor
            sizey = sizex / aspect_ratio  # Adjust height proportionally
        else:
            # Logo is taller than it is wide, or square
            sizey = 3 * scale_factor  # Adjust height with scaling factor
            sizex = sizey * aspect_ratio  # Adjust width proportionally

        # Convert the logo to base64
        logo_base64 = image_to_base64(team_logo)

        # Add the logo above the bar, preserving aspect ratio, with reduced y-offset
        fig.add_layout_image(
            dict(
                source=f'data:image/png;base64,{logo_base64}',
                xref="x",
                yref="y",
                x=team,  # Align with team on x-axis
                y=points + y_offset,  # Reduced y-offset
                sizex=sizex,  # Set the width based on aspect ratio and scaling
                sizey=sizey,  # Set the height based on aspect ratio and scaling
                xanchor="center",
                yanchor="bottom",
                layer="above"
            )
        )

    # Add a dotted line for the average points
    fig.add_shape(
        type='line',
        x0=-0.5,  # Start before the first bar
        x1=len(points_per_team) - 0.5,  # End after the last bar
        y0=average_points,
        y1=average_points,
        line=dict(color="white", width=2, dash="dot")  # White dotted line
    )

    # Update the layout of the chart
    fig.update_layout(
        title="Points Earned from Teams",
        xaxis_title="Teams",
        yaxis_title="Points",
        height=600,
        width=1000,
        template="plotly_white",
        margin=dict(t=100),  # Increase the top margin to make space for logos
        xaxis=dict(showticklabels=False),  # Remove the x-axis labels
        yaxis=dict(range=[0, points_per_team['Points'].max() * 1.2])  # Extend the y-axis range by 20% to allow space for logos
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)