import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde

# Define the ColorBrewer Set2 color palette
color_palette = {
    "Andreas": "rgba(102, 194, 165, 0.85)",  # light green
    "Gerd": "rgba(252, 141, 98, 0.85)",      # light orange
    "Geri": "rgba(141, 160, 203, 0.85)",     # light blue
    "Hermann": "rgba(231, 138, 195, 0.85)",  # light pink
    "Johnny": "rgba(166, 216, 84, 0.85)",    # light lime green
    "Moddy": "rgba(255, 217, 47, 0.85)",     # light yellow
    "Samson": "rgba(229, 196, 148, 0.85)",   # light brown
    "Gray": "rgba(179, 179, 179, 0.85)",     # light gray for default bars
    "density_curve": "blue",                 # blue for density curve
    "mean": "rgba(255, 255, 255, 1)",        # white for mean line
    "default_std_dev": "rgba(255, 217, 47, 1)", # light yellow for std dev by default
    "default_mode": "rgba(166, 216, 84, 1)", # lime green for mode by default
    "default_median": "rgba(231, 138, 195, 1)" # light pink for median by default
}

def display_season_density_plot(matchday, rankings_df, selected_players):
    st.subheader("Density Plot")

    # Filter data for the selected players up to the selected matchday
    filtered_df = rankings_df[(rankings_df['Spieltag'] <= matchday) & (rankings_df['Name'].isin(selected_players))]

    # Extract the points scored by each player
    points = filtered_df['Punkte']

    # Assign dynamic colors based on the selected player
    if len(selected_players) == 1 and selected_players[0] != 'All':
        player_color = color_palette[selected_players[0]]
        bars_color = player_color

        # Dynamically assign colors to other lines to avoid conflicts
        std_dev_color = color_palette["default_std_dev"] if player_color != color_palette["default_std_dev"] else color_palette["Geri"]
        median_color = color_palette["default_median"] if player_color != color_palette["default_median"] else color_palette["Andreas"]
        mode_color = color_palette["default_mode"] if player_color != color_palette["default_mode"] else color_palette["Hermann"]

    else:
        bars_color = color_palette["Gray"]
        std_dev_color = color_palette["default_std_dev"]
        median_color = color_palette["default_median"]
        mode_color = color_palette["default_mode"]

    # Create the histogram using Plotly
    fig = go.Figure()

    # Add histogram bars
    fig.add_trace(go.Bar(
        x=list(range(0, 22)),
        y=[len(points[points == i]) for i in range(22)],
        marker=dict(color=bars_color, line=dict(color='white', width=1)),
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
        line=dict(color=median_color, dash="dot"),
        hoverinfo='skip',
    ))

    fig.add_trace(go.Scatter(
        x=[mode_value, mode_value],
        y=[0, max(y_values * len(points))],
        mode="lines",
        name=f"Mode: {mode_value:.1f}",
        line=dict(color=mode_color, dash="dot"),
        hoverinfo='skip',
    ))

    # Add standard deviation lines
    fig.add_trace(go.Scatter(
        x=[mean_value - std_dev, mean_value + std_dev],
        y=[0, 0],
        mode="lines+markers",
        marker=dict(color=std_dev_color, symbol="x", size=10),
        line=dict(color=std_dev_color, dash="solid", width=2),
        name="1 Std Dev",
        hoverinfo='skip',
    ))

    fig.add_trace(go.Scatter(
        x=[mean_value - 2 * std_dev, mean_value + 2 * std_dev],
        y=[0, 0],
        mode="lines+markers",
        marker=dict(color=std_dev_color, symbol="x", size=10),
        line=dict(color=std_dev_color, dash="dot", width=2),
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
