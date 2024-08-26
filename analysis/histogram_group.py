import streamlit as st
import plotly.graph_objs as go
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

def display_matchday_histogram(matchday, rankings_df, selected_players):
    st.subheader("Matchday Histogram")

    # Filter data for the selected matchday
    filtered_df = rankings_df[(rankings_df['Spieltag'] == matchday) & (rankings_df['Name'].isin(selected_players))]

    # Sort players alphabetically
    filtered_df = filtered_df.sort_values('Name')

    # Extract the points scored by each player
    points = filtered_df['Punkte']
    players = filtered_df['Name']

    # Calculate average points for the matchday
    matchday_avg = points.mean()

    # Calculate average points for the season up to this matchday
    season_avg = rankings_df[(rankings_df['Spieltag'] <= matchday) & (rankings_df['Name'].isin(selected_players))]['Punkte'].mean()

    # Create the histogram using Plotly
    fig = go.Figure()

    # Add bars for each player
    fig.add_trace(go.Bar(
        x=players, 
        y=points, 
        marker=dict(color=[color_palette[player] for player in players])
    ))

    # Add dotted lines for matchday and season averages
    fig.add_trace(go.Scatter(
        x=[players.min(), players.max()],
        y=[matchday_avg, matchday_avg],
        mode="lines",
        name=f"Matchday Avg: {matchday_avg:.1f}",
        line=dict(color="blue", width=2, dash="dot"),
    ))

    fig.add_trace(go.Scatter(
        x=[players.min(), players.max()],
        y=[season_avg, season_avg],
        mode="lines",
        name=f"Season Avg: {season_avg:.1f}",
        line=dict(color="red", width=2, dash="dot"),
    ))

    # Update layout
    fig.update_layout(
        title_text=f"Points Scored by Players on Matchday {matchday}",
        xaxis_title="Players",
        yaxis_title="Points",
        yaxis=dict(
            autorange=True,
        ),
        xaxis=dict(
            tickangle=15,
        ),
        barmode="group",
        height=400,
        width=600,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
