import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from scipy.stats import norm

# Function to filter matches based on the selected season and matchday
def filter_matches_for_season(df, selected_season, matchday):
    if selected_season == '2023/24':
        # Exclude data from the selected matchday for the 2023/24 season
        return df[(df['Season'] == selected_season) & (df['Matchday'] < matchday)]
    else:
        # Include data from the selected matchday for previous seasons (2005/06 to 2022/23)
        return df[(df['Season'] == selected_season) & (df['Matchday'] <= matchday)]

def display_histogram(df, selected_season, selected_matchday):
    st.subheader("Goals Scored per Matchday Histogram")

    # Filter the data using the updated filtering function
    df_filtered = filter_matches_for_season(df, selected_season, selected_matchday)

    # Aggregate the total goals for each matchday
    total_goals_per_matchday = df_filtered.groupby('Matchday').apply(
        lambda x: x['Home Goals'].sum() + x['Away Goals'].sum()
    ).reset_index(name='Total Goals')

    # Create the static histogram
    fig = go.Figure()

    # Add histogram with bins of 1 goal
    fig.add_trace(go.Histogram(
        x=total_goals_per_matchday['Total Goals'],
        xbins=dict(
            start=(min(total_goals_per_matchday['Total Goals'])) - 0.5,  # Start half a goal before the minimum for proper bin alignment
            end=(max(total_goals_per_matchday['Total Goals'])) + 0.5,  # End half a goal after the maximum for proper bin alignment
            size=1  # Size of 1 to ensure each bin represents a single goal
        ),
        histnorm='probability density',
        name='Histogram',
        marker=dict(
            color='rgba(255, 99, 132, 0.6)',  # Pastel red with transparency
            line=dict(color='rgba(255, 99, 132, 1.0)', width=1),
        ),
    ))

    # Fit a normal distribution to the data
    mu, std = norm.fit(total_goals_per_matchday['Total Goals'])

    # Generate x values for the density curve
    x_values = np.linspace(min(total_goals_per_matchday['Total Goals']), max(total_goals_per_matchday['Total Goals']), 100)
    y_values = norm.pdf(x_values, mu, std)

    # Add density curve
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode='lines',
        line=dict(color='rgba(75, 192, 192, 0.6)', width=2),  # Pastel green with transparency
        name='Density Curve'
    ))

    # Add mean, median, and mode
    mean_value = total_goals_per_matchday['Total Goals'].mean()
    median_value = total_goals_per_matchday['Total Goals'].median()
    mode_value = total_goals_per_matchday['Total Goals'].mode()[0]

    fig.add_trace(go.Scatter(
        x=[mean_value, mean_value],
        y=[0, max(y_values)],
        mode="lines",
        line=dict(color="rgba(255, 206, 86, 0.6)", dash="dash"),  # Pastel yellow with transparency
        name=f"Mean: {mean_value:.2f}"
    ))

    fig.add_trace(go.Scatter(
        x=[median_value, median_value],
        y=[0, max(y_values)],
        mode="lines",
        line=dict(color="rgba(54, 162, 235, 0.6)", dash="dash"),  # Pastel blue with transparency
        name=f"Median: {median_value:.2f}"
    ))

    fig.add_trace(go.Scatter(
        x=[mode_value, mode_value],
        y=[0, max(y_values)],
        mode="lines",
        line=dict(color="rgba(153, 102, 255, 0.6)", dash="dash"),  # Pastel purple with transparency
        name=f"Mode: {mode_value:.2f}"
    ))

    # Add standard deviations
    fig.add_trace(go.Scatter(
        x=[mu - std, mu + std],
        y=[0, 0],
        mode="lines+markers",
        line=dict(color="rgba(255, 159, 64, 0.6)", dash="dot"),  # Pastel orange with transparency
        marker=dict(color="rgba(255, 159, 64, 1.0)", size=10, symbol="x"),  # Darker orange for markers
        name="1 Std Dev"
    ))

    fig.add_trace(go.Scatter(
        x=[mu - 2*std, mu + 2*std],
        y=[0, 0],
        mode="lines+markers",
        line=dict(color="rgba(255, 159, 64, 0.6)", dash="dot"),  # Pastel orange with transparency
        marker=dict(color="rgba(255, 159, 64, 1.0)", size=10, symbol="x"),  # Darker orange for markers
        name="2 Std Dev"
    ))

    # Customize layout
    fig.update_layout(
        title=f"Distribution of Total Goals per Matchday (Season: {selected_season})",
        xaxis=dict(title="Total Goals per Matchday"),
        yaxis=dict(title="Density"),
        height=700,  # Increase height to accommodate the legend
        width=800,
        bargap=0.2,
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="top",
            y=-0.2,  # Position the legend below the chart
            xanchor="center",
            x=0.5
        )
    )

    # Display the static figure
    st.plotly_chart(fig)