import streamlit as st
import plotly.graph_objs as go
import pandas as pd

def display_line_plot(matchdays_df, selected_players):
    st.subheader("Line Plot: Goals Prediction vs. Actual Goals")

    # Initialize lists to store data
    player_lines = []
    player_colors = {}
    predicted_goals = []
    actual_goals = []
    
    # Define color palette for players
    colors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', '#9467bd', '#8c564b', '#e377c2']
    
    # Calculate predicted and actual goals for each player
    for i, player in enumerate(selected_players):
        pred_col = f'{player} Predicted Goals'
        player_color = colors[i % len(colors)]
        
        # Player's predicted goals
        player_predicted_goals = matchdays_df.groupby('Matchday')[pred_col].sum()
        player_lines.append(go.Scatter(
            x=player_predicted_goals.index,
            y=player_predicted_goals.values,
            mode='lines+markers',
            name=player,
            line=dict(color=player_color),
            marker=dict(size=6),
        ))
        player_colors[player] = player_color
    
    # Calculate the group average predicted goals
    group_predicted_goals = matchdays_df[[f'{player} Predicted Goals' for player in selected_players]].sum(axis=1) / len(selected_players)
    
    # Calculate actual goals
    actual_goals = matchdays_df.groupby('Matchday')['Actual Goals'].sum()

    # Calculate season averages
    avg_predicted_goals = group_predicted_goals.mean()
    avg_actual_goals = actual_goals.mean()
    
    # Create the line plot
    fig = go.Figure()
    
    # Add lines for each player
    for line in player_lines:
        fig.add_trace(line)

    # Add group average predicted goals line
    fig.add_trace(go.Scatter(
        x=group_predicted_goals.index,
        y=group_predicted_goals.values,
        mode='lines',
        name='Group Average Predicted Goals',
        line=dict(color='black', dash='dash'),
    ))

    # Add actual goals line
    fig.add_trace(go.Scatter(
        x=actual_goals.index,
        y=actual_goals.values,
        mode='lines',
        name='Actual Goals',
        line=dict(color='red', dash='dash'),
    ))

    # Add dotted lines for average goals
    fig.add_trace(go.Scatter(
        x=[group_predicted_goals.index.min(), group_predicted_goals.index.max()],
        y=[avg_predicted_goals] * 2,
        mode='lines',
        name='Average Predicted Goals (Season)',
        line=dict(color='blue', dash='dot'),
    ))

    fig.add_trace(go.Scatter(
        x=[actual_goals.index.min(), actual_goals.index.max()],
        y=[avg_actual_goals] * 2,
        mode='lines',
        name='Average Actual Goals (Season)',
        line=dict(color='green', dash='dot'),
    ))

    # Add shaded area for prediction range
    min_predicted_goals = matchdays_df[[f'{player} Predicted Goals' for player in selected_players]].min(axis=1)
    max_predicted_goals = matchdays_df[[f'{player} Predicted Goals' for player in selected_players]].max(axis=1)
    
    fig.add_trace(go.Scatter(
        x=pd.concat([group_predicted_goals.index, group_predicted_goals.index[::-1]]),
        y=pd.concat([min_predicted_goals, max_predicted_goals[::-1]]),
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Prediction Range'
    ))

    # Update layout
    fig.update_layout(
        title_text='Goals Prediction vs. Actual Goals',
        xaxis_title='Matchday',
        yaxis_title='Number of Goals',
        height=600,
        width=800,
        showlegend=True,
        legend=dict(x=0, y=1.0),
    )

    # Display the line plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)
