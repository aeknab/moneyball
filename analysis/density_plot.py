import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde

# Define the ColorBrewer Set2 color palette
color_palette = {
    "bars": "rgba(179, 179, 179, 0.75)",         # light gray with 75% transparency
    "density_curve": "rgba(102, 194, 165, 1)",   # light green fully opaque
    "mean": "rgba(252, 141, 98, 1)",             # light orange fully opaque
    "median": "rgba(231, 138, 195, 1)",          # light pink fully opaque
    "mode": "rgba(166, 216, 84, 1)",             # lime green fully opaque
    "std_dev": "rgba(255, 217, 47, 1)"           # light yellow fully opaque
}

def display_season_density_plot(matchday, rankings_df, selected_players):
    st.subheader("Density Plot")

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
        marker=dict(color=color_palette["bars"], line=dict(color='white', width=1)),
        hovertemplate='%{x} Points, %{y} times',
        showlegend=False  # Hide from legend
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
        line=dict(color=color_palette["density_curve"], width=2),
        name='Density Curve',
        hoverinfo='skip',  # Ensure no "trace 0"
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
        name=f"Mean: {mean_value:.1f}",
        line=dict(color=color_palette["mean"], dash="dot"),
        hoverinfo='skip',
    ))

    fig.add_trace(go.Scatter(
        x=[median_value, median_value],
        y=[0, max(y_values * len(points))],
        mode="lines",
        name=f"Median: {median_value:.1f}",
        line=dict(color=color_palette["median"], dash="dot"),
        hoverinfo='skip',
    ))

    fig.add_trace(go.Scatter(
        x=[mode_value, mode_value],
        y=[0, max(y_values * len(points))],
        mode="lines",
        name=f"Mode: {mode_value:.1f}",
        line=dict(color=color_palette["mode"], dash="dot"),
        hoverinfo='skip',
    ))

    # Add standard deviation lines
    fig.add_trace(go.Scatter(
        x=[mean_value - std_dev, mean_value + std_dev],
        y=[0, 0],
        mode="lines+markers",
        marker=dict(color=color_palette["std_dev"], symbol="x", size=10),
        line=dict(color=color_palette["std_dev"], dash="solid", width=2),
        name="1 Std Dev",
        hoverinfo='skip',
    ))

    fig.add_trace(go.Scatter(
        x=[mean_value - 2 * std_dev, mean_value + 2 * std_dev],
        y=[0, 0],
        mode="lines+markers",
        marker=dict(color=color_palette["std_dev"], symbol="x", size=10),
        line=dict(color=color_palette["std_dev"], dash="dot", width=2),
        name="2 Std Dev",
        hoverinfo='skip',
    ))

    # Update layout
    fig.update_layout(
        title_text=f"Distribution of Points Scored in Season",
        xaxis_title="Points",
        yaxis_title="Frequency",
        xaxis=dict(
            tickvals=list(range(0, 22, 2)),  # Show ticks at every 2 points
            tickangle=0,  # Keep labels horizontal
            title_standoff=5,  # Reduce standoff for x-axis
        ),
        yaxis=dict(
            title_standoff=10,  # Reduce standoff for y-axis
        ),
        height=400,
        width=600,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=10),  # Reduce legend font size
            itemsizing='constant',  # Keep items uniform size
            traceorder="normal"  # Keep the order of traces in the legend
        )
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
