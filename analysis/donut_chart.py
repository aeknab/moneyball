import streamlit as st
import plotly.graph_objs as go
import pandas as pd
from groups.utils import calculate_points  # Adjusted import

# Define the new color palette for the chart
colors = ['#c4c4c4', '#fffacd', '#ffa07a', '#ff7f7f']
border_colors = ['#999999', '#ffd700', '#ff4500', '#d32f2f']

def display_donut_chart(matchdays_df, selected_players, matchday):
    st.subheader("Donut Chart: Prediction Accuracy")

    # Initialize a dictionary to count occurrences of each outcome
    outcome_counts = {
        '0 Points': 0,
        '2 Points': 0,
        '3 Points': 0,
        '4 Points': 0
    }

    total_predictions = 0

    # Iterate over all matchdays up to the selected matchday
    filtered_matches = matchdays_df[matchdays_df["Matchday"] <= matchday]
    for _, match in filtered_matches.iterrows():
        home_team = match['Home Team']
        away_team = match['Away Team']
        home_goals_actual = match['Home Goals']
        away_goals_actual = match['Away Goals']

        # Iterate over the selected players
        for player in selected_players:
            home_goals_pred = match[f"{player} Home Goals Predicted"]
            away_goals_pred = match[f"{player} Away Goals Predicted"]

            # Calculate the points for this prediction
            points = calculate_points(home_goals_pred, away_goals_pred, home_goals_actual, away_goals_actual)
            total_predictions += 1

            if points == 0:
                outcome_counts['0 Points'] += 1
            elif points == 2:
                outcome_counts['2 Points'] += 1
            elif points == 3:
                outcome_counts['3 Points'] += 1
            elif points == 4:
                outcome_counts['4 Points'] += 1

    # Calculate the percentages for the donut chart
    for outcome in outcome_counts:
        outcome_counts[outcome] = (outcome_counts[outcome] / total_predictions) * 100

    # Create the donut chart using Plotly
    fig = go.Figure(data=[go.Pie(
        labels=['0 Points', '2 Points', '3 Points', '4 Points'],
        values=[outcome_counts['0 Points'], outcome_counts['2 Points'], outcome_counts['3 Points'], outcome_counts['4 Points']],
        hole=.4,  # Create a donut chart
        marker=dict(colors=colors, line=dict(color=border_colors, width=2)),
        textinfo='percent',
        textfont=dict(size=18, color='black', family='Arial', weight='bold'),
        hoverinfo='label+value+text',
        texttemplate='%{percent:.1%}',
        hovertemplate='%{label}:<br>%{value:.1f}%<extra></extra>',
        sort=False,  # Explicitly do not sort slices by size
        direction='clockwise',  # Ensure sections are placed in a clockwise order
        rotation=90  # Start "0 Points" at the 12 o'clock position
    )])

    # Update layout
    fig.update_layout(
        title_text=f"Prediction Accuracy for {' and '.join(selected_players)} up to Matchday {matchday}",
        height=600,
        width=600,
        showlegend=True,
    )

    # Display the donut chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
