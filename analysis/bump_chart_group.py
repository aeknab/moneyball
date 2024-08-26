import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Define a color palette for players
color_palette = {
    "Andreas": "#1f77b4",
    "Gerd": "#ff7f0e",
    "Geri": "#2ca02c",
    "Hermann": "#d62728",
    "Johnny": "#9467bd",
    "Moddy": "#8c564b",
    "Samson": "#e377c2"
}

def display_group_bump_chart(matchday, rankings_df, selected_players):
    st.subheader("Bump Chart")

    # Filter rankings data up to and including the selected matchday
    filtered_rankings_df = rankings_df[(rankings_df['Spieltag'] <= matchday) & (rankings_df['Name'].isin(selected_players))]

    # Create a pivot table with players as rows and matchdays as columns, with rank as values
    rank_pivot = filtered_rankings_df.pivot(index='Name', columns='Spieltag', values='Rang')

    # Create a Plotly figure
    fig = go.Figure()

    # Add a trace for each player
    for player in rank_pivot.index:
        fig.add_trace(go.Scatter(
            x=rank_pivot.columns,
            y=rank_pivot.loc[player],
            mode='lines+markers',
            name=player,
            marker=dict(size=8, color=color_palette.get(player, '#1f77b4')),  # Use player-specific color
            line=dict(width=2, color=color_palette.get(player, '#1f77b4'))  # Use player-specific color
        ))

    # Customize the layout
    fig.update_layout(
        title_text=f'Group Player Rankings - Bump Chart (up to Matchday {matchday})',
        xaxis_title='Matchday',
        yaxis_title='Rank',
        yaxis=dict(autorange='reversed', dtick=1),  # Invert y-axis and set tick interval to 1
        xaxis=dict(dtick=1),  # Ensure matchdays are clearly labeled
        template='plotly_white',  # Optional: Use the 'plotly_white' theme for a clean look
        height=600,  # Adjust height if needed
        margin=dict(l=50, r=20, t=50, b=50)  # Adjust margins if needed
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
