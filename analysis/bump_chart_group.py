import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Define the new ColorBrewer Set2 color palette for players with 75% transparency
color_palette = {
    "Andreas": "rgba(102, 194, 165, 0.75)",  # light green
    "Gerd": "rgba(252, 141, 98, 0.75)",      # light orange
    "Geri": "rgba(141, 160, 203, 0.75)",     # light blue
    "Hermann": "rgba(231, 138, 195, 0.75)",  # light pink
    "Johnny": "rgba(166, 216, 84, 0.75)",    # light lime green
    "Moddy": "rgba(255, 217, 47, 0.75)",     # light yellow
    "Samson": "rgba(229, 196, 148, 0.75)"    # light brown
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
            marker=dict(size=8, color=color_palette.get(player, 'rgba(102, 194, 165, 0.75)')),  # Use player-specific color
            line=dict(width=2, color=color_palette.get(player, 'rgba(102, 194, 165, 0.75)'))  # Use player-specific color
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
