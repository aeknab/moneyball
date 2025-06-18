import streamlit as st
import plotly.graph_objs as go
import pandas as pd

# Function to calculate the heat map data for both predictions and actual results
def calculate_heat_map_data(matchdays_df, selected_players, segment_size=5):
    """Calculate the data for heatmaps and trends of Group Predictions and Bundesliga Actual Results."""
    
    # Initialize dataframes to accumulate counts for home-away goal combinations (for group predictions)
    goal_combinations = pd.DataFrame(0, index=range(9), columns=range(9))  # Extend to 9 (0-8)
    goal_combinations_actual = pd.DataFrame(0, index=range(9), columns=range(9))  # For actual goals
    
    # Variable to store trends over segments of matchdays
    trend_data = {
        'predictions': [],
        'actual': [],
        'matchdays': []
    }

    for player in selected_players:
        home_col = f'{player} Home Goals Predicted'
        away_col = f'{player} Away Goals Predicted'
        
        # Loop over segments of matchdays (e.g., last 5 matchdays)
        for i in range(0, len(matchdays_df), segment_size):
            matchdays_segment = matchdays_df.iloc[i:i+segment_size]
            
            # Count occurrences of each home-away goal combination for the segment
            counts = matchdays_segment.groupby([home_col, away_col]).size()
            for (home_goals, away_goals), count in counts.items():
                h_index = min(home_goals, 8)  # Treat 8+ goals as 8
                a_index = min(away_goals, 8)  # Treat 8+ goals as 8
                goal_combinations.at[h_index, a_index] += count

            # For actual results
            actual_home_goals = matchdays_segment['Home Goals']
            actual_away_goals = matchdays_segment['Away Goals']
            for h_goal, a_goal in zip(actual_home_goals, actual_away_goals):
                h_index = h_goal if h_goal < 8 else 8
                a_index = a_goal if a_goal < 8 else 8
                goal_combinations_actual.at[h_index, a_index] += 1

            # Collect trend data over the segment
            trend_data['predictions'].append(goal_combinations.sum().sum())
            trend_data['actual'].append(goal_combinations_actual.sum().sum())
            trend_data['matchdays'].append(f"Matchdays {i+1}-{i+segment_size}")

    # Determine the most common scores (for actual and predicted)
    top_pred_scores = goal_combinations.stack().nlargest(3)
    top_actual_scores = goal_combinations_actual.stack().nlargest(3)

    return goal_combinations, goal_combinations_actual, trend_data, top_pred_scores, top_actual_scores

# Function to display the heatmaps for group predictions and actual Bundesliga results
def display_group_heat_map(matchdays_df, selected_players):
    st.subheader("Heatmaps")

    # Calculate the heatmap data
    goal_combinations, goal_combinations_actual, trend_data, top_pred_scores, top_actual_scores = calculate_heat_map_data(matchdays_df, selected_players)

    # Create two columns for side-by-side heatmaps
    heatmap_col1, heatmap_col2 = st.columns(2)

    # Heatmap for Group Predictions
    with heatmap_col1:
        players_display = ', '.join(selected_players)
        st.markdown(f"<h4 style='font-size:16px'>{players_display} Predictions Heatmap</h4>", unsafe_allow_html=True)

        # Convert index and columns to strings for labeling
        goal_combinations.index = goal_combinations.index.astype(str)
        goal_combinations.columns = goal_combinations.columns.astype(str)

        # Create the heatmap using Plotly
        fig = go.Figure(data=go.Heatmap(
            z=goal_combinations.values,
            x=goal_combinations.columns,
            y=goal_combinations.index,
            colorscale='Viridis',
            showscale=False,
            text=goal_combinations.values,
            texttemplate="%{text}",
            hovertemplate="Home Goals: %{y}<br>Away Goals: %{x}<br>Count: %{z}<extra></extra>",
            textfont={"size": 12},
        ))

        # Update layout with strict axis ranges and no extra space
        fig.update_layout(
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(
                title="Away Goals",
                range=[-0.5, 8.5],  # Extend the range to ensure full visibility
                scaleanchor="y",
                constrain="domain",
                tickmode="array",
                tickvals=list(range(9)),  # Only show ticks from 0 to 8
                dtick=1,
                ticks="inside",  # Move ticks inside the axis
                position=0,  # Set position to adjust the placement
            ),
            yaxis=dict(
                title="Home Goals",
                range=[-0.5, 8.5],  # Extend the range to ensure full visibility
                tickmode="array",
                tickvals=list(range(9)),  # Only show ticks from 0 to 8
                dtick=1,
            ),
            height=400,
            width=400,  # Ensure square layout
            plot_bgcolor='rgba(0,0,0,0)',  # Remove background color
            paper_bgcolor='rgba(0,0,0,0)'  # Remove paper background color
        )

        st.plotly_chart(fig, use_container_width=True)

    # Heatmap for Bundesliga Actual Results
    with heatmap_col2:
        st.markdown("<h4 style='font-size:16px'>Bundesliga Actual Results Heatmap</h4>", unsafe_allow_html=True)

        # Convert index and columns to strings for labeling
        goal_combinations_actual.index = goal_combinations_actual.index.astype(str)
        goal_combinations_actual.columns = goal_combinations_actual.columns.astype(str)

        # Create the heatmap using Plotly
        fig_actual = go.Figure(data=go.Heatmap(
            z=goal_combinations_actual.values,
            x=goal_combinations_actual.columns,
            y=goal_combinations_actual.index,
            colorscale='Viridis',
            showscale=False,
            text=goal_combinations_actual.values,
            texttemplate="%{text}",
            hovertemplate="Home Goals: %{y}<br>Away Goals: %{x}<br>Count: %{z}<extra></extra>",
            textfont={"size": 12},
        ))

        # Update layout with strict axis ranges and no extra space
        fig_actual.update_layout(
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(
                title="Away Goals",
                range=[-0.5, 8.5],  # Extend the range to ensure full visibility
                scaleanchor="y",
                constrain="domain",
                tickmode="array",
                tickvals=list(range(9)),  # Only show ticks from 0 to 8
                dtick=1,
                ticks="inside",  # Move ticks inside the axis
                position=0,  # Set position to adjust the placement
            ),
            yaxis=dict(
                title="Home Goals",
                range=[-0.5, 8.5],  # Extend the range to ensure full visibility
                tickmode="array",
                tickvals=list(range(9)),  # Only show ticks from 0 to 8
                dtick=1,
            ),
            height=400,
            width=400,  # Ensure square layout
            plot_bgcolor='rgba(0,0,0,0)',  # Remove background color
            paper_bgcolor='rgba(0,0,0,0)'  # Remove paper background color
        )

        st.plotly_chart(fig_actual, use_container_width=True)