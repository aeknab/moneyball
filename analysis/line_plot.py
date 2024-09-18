import streamlit as st
import plotly.graph_objs as go
import pandas as pd
from scipy.stats import linregress

def calculate_line_plot_data(matchdays_df, selected_players, matchday):
    """Calculate the data for the line plot of goals prediction vs. actual goals."""
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
        # Set color and alpha for the player
        if len(selected_players) == 1 and player == selected_players[0]:
            # Selected player
            player_alpha = 1.0
        else:
            # Other players
            player_alpha = 0.75
        player_color = color_palette_template.get(player, color_palette_template['Gray']).format(alpha=player_alpha)
        player_colors[player] = player_color
        
        # Required columns for the player
        required_columns = [f'{player} Home Goals Predicted', f'{player} Away Goals Predicted']
        missing_columns = [col for col in required_columns if col not in matchdays_df.columns]
        if missing_columns:
            st.error(f"Missing data for {player}: {', '.join(missing_columns)}")
            continue  # Skip to the next player
        
        # Calculate player's predicted goals by summing home and away goals for each matchday
        player_predicted_goals = matchdays_df.groupby('Matchday')[required_columns].sum().sum(axis=1)
        
        predicted_goals[player] = player_predicted_goals  # Store this player's predicted goals
        
        # Only add the selected player's line to player_lines
        if len(selected_players) == 1 and player == selected_players[0]:
            player_lines.append(go.Scatter(
                x=player_predicted_goals.index,
                y=player_predicted_goals.values,
                mode='lines+markers',
                name=player,
                line=dict(color=player_color),
                marker=dict(size=6, color=player_color),
            ))
        elif len(selected_players) > 1 or selected_players == list(player_names):
            # If multiple players are selected or 'All', add all players' lines
            player_lines.append(go.Scatter(
                x=player_predicted_goals.index,
                y=player_predicted_goals.values,
                mode='lines+markers',
                name=player,
                line=dict(color=player_color),
                marker=dict(size=6, color=player_color),
            ))
    
    # Check if we have any players' data
    if predicted_goals.empty:
        st.warning("No player data available to plot.")
        return None
    
    # Calculate actual goals
    actual_goals = matchdays_df.groupby('Matchday')[['Home Goals', 'Away Goals']].sum().sum(axis=1)
    
    # Exclude selected player from group calculations if an individual player is selected
    if len(selected_players) == 1:
        selected_player = selected_players[0]
        predicted_goals_for_group = predicted_goals.drop(columns=[selected_player])
    else:
        predicted_goals_for_group = predicted_goals
    
    # Calculate group's season average predicted goals (excluding selected player if applicable)
    avg_predicted_goals = predicted_goals_for_group.mean(axis=1).mean()
    avg_actual_goals = actual_goals.mean()
    
    # For individual player's average predicted goals
    if len(selected_players) == 1:
        player_avg_predicted_goals = predicted_goals[selected_player].mean()
    else:
        player_avg_predicted_goals = None
    
    # Calculate the prediction range using min and max of predicted_goals_for_group for each matchday
    min_predicted_goals = predicted_goals_for_group.min(axis=1)
    max_predicted_goals = predicted_goals_for_group.max(axis=1)
    
    # Calculate the trend over time using group's predicted goals
    if len(predicted_goals_for_group.index) > 1:
        trend_slope, _, _, _, _ = linregress(
            predicted_goals_for_group.index.values.astype(float),
            predicted_goals_for_group.mean(axis=1).values
        )
    else:
        trend_slope = 0  # Not enough data to calculate trend
    
    if trend_slope > 0:
        trend_over_time = "increasing"
        trend_description = "steadily improving"
    elif trend_slope < 0:
        trend_over_time = "decreasing"
        trend_description = "declining"
    else:
        trend_over_time = "stable"
        trend_description = "remaining consistent"
    
    return {
        "player_lines": player_lines,
        "actual_goals": actual_goals,
        "avg_predicted_goals": avg_predicted_goals,
        "avg_actual_goals": avg_actual_goals,
        "min_predicted_goals": min_predicted_goals,
        "max_predicted_goals": max_predicted_goals,
        "player_colors": player_colors,
        "trend_over_time": trend_over_time,
        "trend_description": trend_description,
        "player_avg_predicted_goals": player_avg_predicted_goals,
        "matchday": matchday
    }

def display_line_plot(matchdays_df, selected_players, matchday):
    st.subheader("Line Plot: Goals Prediction vs. Actual Goals")
    
    # Calculate the line plot data
    data = calculate_line_plot_data(matchdays_df, selected_players, matchday)
    
    if data is None:
        return  # Exit if no data is available
    
    # Round the averages to one decimal place
    avg_predicted_goals = round(data["avg_predicted_goals"], 1)
    avg_actual_goals = round(data["avg_actual_goals"], 1)
    if data["player_avg_predicted_goals"] is not None:
        player_avg_predicted_goals = round(data["player_avg_predicted_goals"], 1)
    
    # Create the line plot
    fig = go.Figure()
    
    # Add shaded area for prediction range first (bottom layer)
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
    fig.add_trace(go.Scatter(
        x=[0, 35],
        y=[avg_predicted_goals] * 2,
        mode='lines',
        name=f'Avg Predicted Goals: {avg_predicted_goals}',
        line=dict(color='rgba(0, 128, 255, 0.75)', dash='dot'),
    ))
    
    fig.add_trace(go.Scatter(
        x=[0, 35],
        y=[avg_actual_goals] * 2,
        mode='lines',
        name=f'Avg Actual Goals: {avg_actual_goals}',
        line=dict(color='rgba(255, 0, 0, 0.75)', dash='dot'),
    ))
    
    # If individual player selected, add their average predicted goals line
    if len(selected_players) == 1:
        selected_player = selected_players[0]
        player_color = data['player_colors'][selected_player]
        fig.add_trace(go.Scatter(
            x=[0, 35],
            y=[player_avg_predicted_goals] * 2,
            mode='lines',
            name=f"{selected_player}'s Avg Predicted Goals: {player_avg_predicted_goals}",
            line=dict(color=player_color, dash='dot'),
        ))
    
    # Add actual goals line (next layer)
    fig.add_trace(go.Scatter(
        x=data["actual_goals"].index,
        y=data["actual_goals"].values,
        mode='lines+markers',
        name='Actual Goals',
        line=dict(color='rgba(255,255,255,1.0)'),  # Solid line with 100% opacity
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
        tickvals=list(range(0,36)),
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
    
    # Optionally, display the trend information
    # st.info(f"The trend over time is {data['trend_over_time']}, indicating that predictions are {data['trend_description']}.")
    
    return data["trend_over_time"], data["trend_description"]