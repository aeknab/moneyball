import streamlit as st
import pandas as pd
import plotly.graph_objs as go

def display_group_pie_chart(matchdays_df, selected_players):
    st.subheader("Pie Charts: Group Predictions vs. Bundesliga Actual Results")

    # Aggregate predictions for all selected players
    predictions = {
        'Home Win': 0,
        'Tie': 0,
        'Away Win': 0
    }

    for player in selected_players:
        result_col = f'{player} Result Predicted'
        player_results = matchdays_df[result_col]
        
        predictions['Home Win'] += player_results[player_results == 'Home Win'].count()
        predictions['Tie'] += player_results[player_results == 'Tie'].count()
        predictions['Away Win'] += player_results[player_results == 'Away Win'].count()

    # Aggregate actual Bundesliga results
    results = {
        'Home Win': matchdays_df['Result'][matchdays_df['Result'] == 'Home Win'].count(),
        'Tie': matchdays_df['Result'][matchdays_df['Result'] == 'Tie'].count(),
        'Away Win': matchdays_df['Result'][matchdays_df['Result'] == 'Away Win'].count()
    }

    # Define the colors for the pie chart
    colors = ['#a8e6a1', '#c4c4c4', 'lightyellow']
    border_colors = ['#388e3c', '#999999', '#FFD700']  # Using gold color for away win border

    # Set up the layout for side-by-side pie charts
    pie_col1, pie_col2 = st.columns(2)

    # Pie chart for Group Predictions
    with pie_col1:
        fig_predictions = go.Figure(data=[go.Pie(
            labels=list(predictions.keys()),
            values=list(predictions.values()),
            marker=dict(colors=colors, line=dict(color=border_colors, width=2)),
            textinfo='percent',
            textfont=dict(size=18, color='black', family='Arial'),
            hoverinfo='label+value+text',
            texttemplate='%{percent:.1%}',
            hovertemplate='%{label}:<br>%{value}<extra></extra>',
            sort=False,  # Explicitly do not sort slices by size
            direction='clockwise',  # Ensure sections are placed in a clockwise order
            rotation=90  # Start "Home Win" at the 12 o'clock position
        )])

        # Update layout
        fig_predictions.update_layout(
            title_text="Group Predictions: Wins, Ties, Losses",
            height=500,
            width=500,
            showlegend=True,
        )

        st.plotly_chart(fig_predictions)

    # Pie chart for Bundesliga Actual Results
    with pie_col2:
        fig_results = go.Figure(data=[go.Pie(
            labels=list(results.keys()),
            values=list(results.values()),
            marker=dict(colors=colors, line=dict(color=border_colors, width=2)),
            textinfo='percent',
            textfont=dict(size=18, color='black', family='Arial'),
            hoverinfo='label+value+text',
            texttemplate='%{percent:.1%}',
            hovertemplate='%{label}:<br>%{value}<extra></extra>',
            sort=False,  # Explicitly do not sort slices by size
            direction='clockwise',  # Ensure sections are placed in a clockwise order
            rotation=90  # Start "Home Win" at the 12 o'clock position
        )])

        # Update layout
        fig_results.update_layout(
            title_text="Bundesliga Actual Results: Wins, Ties, Losses",
            height=500,
            width=500,
            showlegend=True,
        )

        st.plotly_chart(fig_results)
