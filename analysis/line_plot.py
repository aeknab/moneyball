import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from scipy.stats import linregress
from numpy.polynomial.polynomial import Polynomial

def calculate_line_plot_data(matchdays_df, selected_players, matchday):
    # Filter matchdays_df up to the selected matchday
    matchdays_df = matchdays_df[matchdays_df['Matchday'] <= matchday]

    # Get all player names
    home_columns = [col for col in matchdays_df.columns if col.endswith('Home Goals Predicted')]
    player_names = set([col.replace(' Home Goals Predicted', '') for col in home_columns])

    predicted_goals = pd.DataFrame()  # To store predicted goals for each player
    player_lines = []
    player_colors = {}

    # Define the color palette template for players
    color_palette_template = {
        "Andreas": "rgba(102, 194, 165, {alpha})",
        "Gerd": "rgba(252, 141, 98, {alpha})",
        "Geri": "rgba(141, 160, 203, {alpha})",
        "Hermann": "rgba(231, 138, 195, {alpha})",
        "Johnny": "rgba(166, 216, 84, {alpha})",
        "Moddy": "rgba(255, 217, 47, {alpha})",
        "Samson": "rgba(229, 196, 148, {alpha})",
        "Gray": "rgba(179, 179, 179, {alpha})"
    }

    # Process all players to calculate predicted goals
    for player in player_names:
        player_color = color_palette_template.get(player, color_palette_template['Gray']).format(alpha=1.0)
        player_colors[player] = player_color
        required_columns = [f'{player} Home Goals Predicted', f'{player} Away Goals Predicted']

        if set(required_columns).issubset(matchdays_df.columns):
            player_predicted_goals = matchdays_df.groupby('Matchday')[required_columns].sum().sum(axis=1)
            predicted_goals[player] = player_predicted_goals

            # If 'All' players are selected, show all lines. If a single player is selected, show only his line and make it thicker.
            if len(selected_players) > 1 or player == selected_players[0]:
                line_width = 4 if player == selected_players[0] else 2
                player_lines.append(go.Scatter(
                    x=player_predicted_goals.index,
                    y=player_predicted_goals.values,
                    mode='lines+markers',
                    name=player,
                    line=dict(color=player_color, width=line_width),
                    marker=dict(size=6, color=player_color),
                ))

    if predicted_goals.empty:
        return None

    # Calculate actual goals
    actual_goals = matchdays_df.groupby('Matchday')[['Home Goals', 'Away Goals']].sum().sum(axis=1)

    # Initialize variables for individual player analysis
    trend_over_time = "N/A"
    trend_description = "Not applicable for all players"
    p = None  # Polynomial coefficients for curve of best fit

    # If only one player is selected, calculate curve of best fit and average predicted goals
    player_avg_predicted_goals = None
    if len(selected_players) == 1:
        player = selected_players[0]
        if player in predicted_goals:
            # Use polynomial regression (degree 2 for a curve of best fit)
            x = predicted_goals[player].index.values
            y = predicted_goals[player].values
            p = Polynomial.fit(x, y, deg=2)

            # Calculate the fitted curve (best fit curve)
            curve_values = p(x)

            # Determine trend based on the curve's first and second derivatives
            if p.deriv(1)(x).mean() > 0:
                trend_over_time = "increasing"
                trend_description = "steadily improving"
            elif p.deriv(1)(x).mean() < 0:
                trend_over_time = "decreasing"
                trend_description = "declining"
            else:
                trend_over_time = "stable"
                trend_description = "remaining consistent"

            # Add Curve of Best Fit to the player's line plot
            player_lines.append(go.Scatter(
                x=predicted_goals[player].index,
                y=curve_values,
                mode='lines',
                name=f"{player}'s Curve of Best Fit",
                line=dict(color=player_colors[player], width=2, dash='dash'),
                showlegend=True
            ))

            # Calculate the player's average predicted goals
            player_avg_predicted_goals = predicted_goals[player].mean()

    # Calculate overestimations, underestimations, and accuracy metrics
    selected_player = selected_players[0] if len(selected_players) == 1 else None
    if selected_player and selected_player in predicted_goals:
        overestimation_count = (predicted_goals[selected_player] > actual_goals + 2).sum()
        underestimation_count = (predicted_goals[selected_player] < actual_goals - 2).sum()
        within_range_count = ((predicted_goals[selected_player] - actual_goals).abs() <= 2).sum()  # Predictions within 2 goal difference

        total_predictions = len(predicted_goals[selected_player])
        overestimation_percentage = (overestimation_count / total_predictions) * 100
        underestimation_percentage = (underestimation_count / total_predictions) * 100
        within_range_percentage = (within_range_count / total_predictions) * 100
    else:
        overestimation_percentage = underestimation_percentage = within_range_percentage = None

    # Exclude selected player from group calculations if an individual player is selected
    predicted_goals_for_group = predicted_goals.drop(columns=[selected_player]) if selected_player else predicted_goals

    avg_predicted_goals = predicted_goals_for_group.mean(axis=1).mean() if not predicted_goals_for_group.empty else None
    avg_actual_goals = actual_goals.mean()

    # Calculate the prediction range using min and max of predicted_goals_for_group for each matchday
    min_predicted_goals = predicted_goals_for_group.min(axis=1) if not predicted_goals_for_group.empty else None
    max_predicted_goals = predicted_goals_for_group.max(axis=1) if not predicted_goals_for_group.empty else None

    # Return all relevant data
    return {
        "player_lines": player_lines,
        "actual_goals": actual_goals,
        "avg_predicted_goals": avg_predicted_goals,
        "avg_actual_goals": avg_actual_goals,
        "min_predicted_goals": min_predicted_goals,
        "max_predicted_goals": max_predicted_goals,
        "player_colors": player_colors,
        "curve_coefficients": p,  # Store polynomial coefficients for further use
        "trend_over_time": trend_over_time,
        "trend_description": trend_description,
        "overestimation_percentage": overestimation_percentage,
        "underestimation_percentage": underestimation_percentage,
        "within_range_percentage": within_range_percentage,
        "player_avg_predicted_goals": player_avg_predicted_goals  # Return player's average predicted goals
    }

def display_line_plot(matchdays_df, selected_players, matchday):
    st.subheader("Line Plot: Goals Prediction vs. Actual Goals")

    # Initialize the figure before any trace is added
    fig = go.Figure()

    # Calculate the line plot data
    data = calculate_line_plot_data(matchdays_df, selected_players, matchday)

    if data is None:
        st.warning("No data available to plot.")
        return

    # Add shaded area for prediction range (bottom layer)
    if data["min_predicted_goals"] is not None and data["max_predicted_goals"] is not None:
        fig.add_trace(go.Scatter(
            x=pd.concat([data["min_predicted_goals"].index.to_series(), data["max_predicted_goals"].index.to_series()[::-1]]),
            y=pd.concat([data["min_predicted_goals"], data["max_predicted_goals"][::-1]]),
            fill='toself',
            fillcolor='rgba(200,200,200,0.50)',  # Light gray with 50% transparency
            line=dict(color='rgba(255,255,255,0)'),
            name='Prediction Range',
            showlegend=True,
        ))

    # Add dotted lines for average goals (next layer)
    if data["avg_predicted_goals"] is not None:
        fig.add_trace(go.Scatter(
            x=[0, 35],
            y=[data["avg_predicted_goals"]] * 2,
            mode='lines',
            name=f'Avg Predicted Goals: {round(data["avg_predicted_goals"], 1)}',
            line=dict(color='rgba(0, 128, 255, 0.75)', dash='dot'),
        ))

    fig.add_trace(go.Scatter(
        x=[0, 35],
        y=[data["avg_actual_goals"]] * 2,
        mode='lines',
        name=f'Avg Actual Goals: {round(data["avg_actual_goals"], 1)}',
        line=dict(color='rgba(255, 0, 0, 0.75)', dash='dot'),
    ))

    # Only add individual player's average predicted goals if one player is selected and data is available
    if data["player_avg_predicted_goals"] is not None and len(selected_players) == 1:
        selected_player = selected_players[0]
        player_color = data['player_colors'][selected_player]
        fig.add_trace(go.Scatter(
            x=[0, 35],
            y=[data["player_avg_predicted_goals"]] * 2,
            mode='lines',
            name=f"{selected_player}'s Avg Predicted Goals: {round(data['player_avg_predicted_goals'], 1)}",
            line=dict(color=player_color, dash='dot'),
        ))

    # Add actual goals line (next layer)
    fig.add_trace(go.Scatter(
        x=data["actual_goals"].index,
        y=data["actual_goals"].values,
        mode='lines+markers',
        name='Actual Goals',
        line=dict(color='rgba(255,255,255,1.0)', width=2.5),
        marker=dict(size=6, color='rgba(255,255,255,1.0)')
    ))

    # Add player lines (top layer)
    for line in data["player_lines"]:
        fig.add_trace(line)

    # Adjust the x-axis range from 0 to 35
    fig.update_layout(
        xaxis=dict(
            range=[0, 35],
            tickmode='linear',
            dtick=1
        )
    )

    # Add vertical line at x=17.5 to mark the midway point
    fig.add_vline(x=17.5, line=dict(color='rgba(255, 255, 255, 0.5)', dash='dot', width=1))

    # Update layout with transparent background and legend below the graph
    fig.update_layout(
        title_text='Goals Prediction vs. Actual Goals',
        xaxis_title='Matchday',
        yaxis_title='Number of Goals',
        height=600,
        width=800,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color='white')
        ),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(14, 17, 23, 0.50)',    # Dark semi-transparent background
    )

    # Adjust x-axis and y-axis to make gridlines visible on dark background
    fig.update_xaxes(
        showgrid=True,
        gridcolor='rgba(255,255,255,0.2)',  # Light gridlines
        zerolinecolor='rgba(255,255,255,0.5)',
        tickfont=dict(color='white'),
        title_font=dict(color='white'),
        tickvals=list(range(0, 36)),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(255,255,255,0.2)',
        zerolinecolor='rgba(255,255,255,0.5)',
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    )

    # Update the plot title and legend font colors
    fig.update_layout(
        title_font=dict(color='white'),
        legend_font=dict(color='white'),
        legend_title_font=dict(color='white'),
    )

    # Display the line plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Optionally, display the trend information for individual players
    #if len(selected_players) == 1:
    #    st.info(f"The trend over time is {data['trend_over_time']}, indicating that predictions are {data['trend_description']}.")