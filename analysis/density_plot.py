import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde

def display_season_density_plot(matchday, rankings_df, selected_players):
    st.subheader("Season Density Plot")

    # Filter data for the selected players up to the selected matchday
    filtered_df = rankings_df[(rankings_df['Spieltag'] <= matchday) & (rankings_df['Name'].isin(selected_players))]

    # Extract the points scored by each player
    points = filtered_df['Punkte']

    # Create the histogram using Plotly
    fig = go.Figure()

    # Add histogram bars
    fig.add_trace(go.Bar(
        x=list(range(0, 22)),
        y=[len(points[points == i]) for i in range(22)],
        marker=dict(color='rgba(0, 123, 255, 0.7)', line=dict(color='white', width=1)),
        hovertemplate='%{x} Points, %{y} times'
    ))

    # Calculate the density curve
    density = gaussian_kde(points)
    x_values = np.linspace(0, 21, 500)
    y_values = density(x_values)

    # Add density curve
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values * len(points),  # Scale to match histogram frequency
        mode='lines',
        line=dict(color='rgba(255, 0, 0, 0.8)', width=2),
        name='Density Curve'
    ))

    # Calculate statistics
    mean_value = points.mean()
    median_value = points.median()
    mode_value = points.mode()[0]
    std_dev = points.std()

    # Add vertical lines for mean, median, mode
    fig.add_trace(go.Scatter(
        x=[mean_value, mean_value],
        y=[0, max(y_values * len(points))],
        mode="lines",
        name=f"Matchday Avg: {mean_value:.1f}",
        line=dict(color="blue", dash="dot")
    ))

    fig.add_trace(go.Scatter(
        x=[median_value, median_value],
        y=[0, max(y_values * len(points))],
        mode="lines",
        name=f"Median: {median_value:.1f}",
        line=dict(color="green", dash="dot")
    ))

    fig.add_trace(go.Scatter(
        x=[mode_value, mode_value],
        y=[0, max(y_values * len(points))],
        mode="lines",
        name=f"Mode: {mode_value:.1f}",
        line=dict(color="purple", dash="dot")
    ))

    # Add standard deviation lines
    for std in range(1, 3):
        fig.add_trace(go.Scatter(
            x=[mean_value - std * std_dev, mean_value + std * std_dev],
            y=[0, 0],
            mode="lines+markers",
            marker=dict(color="orange", symbol="x", size=10),
            line=dict(color="orange", dash="dot"),
            name=f"{std} Std Dev"
        ))

    # Update layout
    fig.update_layout(
        title_text=f"Distribution of Points Scored Up to Matchday {matchday}",
        xaxis_title="Points",
        yaxis_title="Frequency",
        xaxis=dict(
            tickvals=list(range(0, 22)),
            tickangle=30,
        ),
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
