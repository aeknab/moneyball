import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Define the new ColorBrewer Set2 color palette for players with 75% transparency
color_palette = {
    "Andreas": "rgba(102, 194, 165, 0.85)",  # light green
    "Gerd": "rgba(252, 141, 98, 0.85)",      # light orange
    "Geri": "rgba(141, 160, 203, 0.85)",     # light blue
    "Hermann": "rgba(231, 138, 195, 0.85)",  # light pink
    "Johnny": "rgba(166, 216, 84, 0.85)",    # light lime green
    "Moddy": "rgba(255, 217, 47, 0.85)",     # light yellow
    "Samson": "rgba(229, 196, 148, 0.85)"    # light brown
}

def display_group_table(matchday, rankings_df, selected_players):
    st.subheader("Group Table")

    # Filter rankings data up to and including the selected matchday
    filtered_rankings_df = rankings_df[(rankings_df['Spieltag'] <= matchday) & (rankings_df['Name'].isin(selected_players))]

    # Calculate the total points for each player up to and including the selected matchday
    player_points = filtered_rankings_df.groupby('Name')['Punkte'].sum().reindex(selected_players)

    # Sort the players by their total points
    player_points = player_points.sort_values(ascending=False)

    # Create a Plotly figure
    fig = go.Figure()

    # Add a bar for each player with their specific color
    for player in player_points.index:
        fig.add_trace(go.Bar(
            x=[player_points[player]],
            y=[player],
            orientation='h',
            name=player,
            marker=dict(color=color_palette.get(player, 'rgba(102, 194, 165, 0.85)'))  # Use player-specific color
        ))

    # Update layout for the figure
    fig.update_layout(
        title_text=f'Group League Table - Matchday {matchday}',
        xaxis_title='Points',
        yaxis_title='Players',
        yaxis=dict(autorange='reversed'),  # Invert y-axis to have the top player at the top
        template='plotly_white',  # Optional: Use the 'plotly_white' theme for a clean look
        height=400,  # Adjust height if needed
        margin=dict(l=100, r=20, t=50, b=50)  # Adjust margins if needed
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
