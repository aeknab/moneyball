import streamlit as st
import plotly.graph_objs as go
import pandas as pd

# Define the ColorBrewer Set2 color palette with 75% transparency
color_palette = {
    "Andreas": "rgba(102, 194, 165, 0.85)",  # light green
    "Gerd": "rgba(252, 141, 98, 0.85)",      # light orange
    "Geri": "rgba(141, 160, 203, 0.85)",     # light blue
    "Hermann": "rgba(231, 138, 195, 0.85)",  # light pink
    "Johnny": "rgba(166, 216, 84, 0.85)",    # light lime green
    "Moddy": "rgba(255, 217, 47, 0.85)",     # light yellow
    "Samson": "rgba(229, 196, 148, 0.85)",   # light brown
    "Gray": "rgba(179, 179, 179, 0.85)"      # light gray for other players when a single player is selected
}

def display_matchday_histogram(matchday, rankings_df, selected_players):
    st.subheader("Histogram")

    # Filter data for the selected matchday
    filtered_df = rankings_df[rankings_df['Spieltag'] == matchday]

    # Sort players alphabetically
    filtered_df = filtered_df.sort_values('Name')

    # Extract the points scored by each player
    points = filtered_df['Punkte']
    players = filtered_df['Name']

    # Calculate average points for the matchday
    matchday_avg = points.mean()

    # Calculate season average points up to the selected matchday (without filtering by matchday)
    season_points = rankings_df[rankings_df['Spieltag'] <= matchday]['Punkte']
    total_points = season_points.sum()
    season_avg = total_points / matchday  # Average points per matchday across the season

    # Determine bar colors
    if len(selected_players) == 1 and selected_players[0] != 'All':
        # If a single player is selected, gray out the other players
        bar_colors = [color_palette[player] if player in selected_players else color_palette["Gray"] for player in players]
    else:
        # If "All" is selected, use the normal colors
        bar_colors = [color_palette[player] for player in players]

    # Create the histogram using Plotly
    fig = go.Figure()

    # Add bars for each player
    fig.add_trace(go.Bar(
        x=players,
        y=points,
        marker=dict(color=bar_colors),
        hovertemplate='<b>Points:</b> %{y}<br><b>MD Rank:</b> %{customdata[0]}<extra></extra>',
        customdata=[(i+1,) for i in range(len(players))],  # Add rank information
        showlegend=False  # Hide this trace from the legend
    ))

    # Add dotted lines for matchday and season averages
    fig.add_trace(go.Scatter(
        x=[players.iloc[0], players.iloc[-1]],  # Ensure the lines span the entire width of the bars
        y=[matchday_avg, matchday_avg],
        mode="lines",
        name=f"Matchday Avg: {matchday_avg:.1f}",
        line=dict(color="blue", width=2, dash="dot"),
        showlegend=True
    ))

    fig.add_trace(go.Scatter(
        x=[players.iloc[0], players.iloc[-1]],  # Ensure the lines span the entire width of the bars
        y=[season_avg, season_avg],
        mode="lines",
        name=f"Season Avg: {season_avg:.1f}",
        line=dict(color="white", width=2, dash="dot"),
        showlegend=True
    ))

    # Update layout with adjusted standoff and legend position
    fig.update_layout(
        title_text=f"Points Scored on Matchday {matchday}",
        xaxis_title="Players",
        yaxis_title="Points",
        yaxis=dict(
            autorange=True,
            title_standoff=10,  # Standoff for y-axis
        ),
        xaxis=dict(
            tickangle=15,
            title_standoff=5,  # Further reduced standoff for x-axis
        ),
        barmode="group",
        height=400,
        width=600,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,  # Push the legend down slightly
            xanchor="center",
            x=0.5
        )
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
