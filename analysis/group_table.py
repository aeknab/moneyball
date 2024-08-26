import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Define a color palette for players (use the same palette as in the bump chart)
color_palette = {
    "Andreas": "#1f77b4",
    "Gerd": "#ff7f0e",
    "Geri": "#2ca02c",
    "Hermann": "#d62728",
    "Johnny": "#9467bd",
    "Moddy": "#8c564b",
    "Samson": "#e377c2"
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
            marker=dict(color=color_palette.get(player, '#1f77b4'))  # Use player-specific color
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
