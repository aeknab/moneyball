import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from PIL import Image
import base64

def image_to_base64(img_path):
    """Convert image to base64 string."""
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def display_group_pie_chart(matchdays_df, selected_players):
    st.subheader("Pie Charts")

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

    # Define the colors with 85% transparency
    colors = ['rgba(168, 230, 161, 0.85)', 'rgba(196, 196, 196, 0.85)', 'rgba(255, 250, 205, 0.85)']
    border_colors = ['rgba(56, 142, 60, 1)', 'rgba(153, 153, 153, 1)', 'rgba(255, 215, 0, 1)']

    # Load the Bundesliga logo
    bundesliga_logo_path = "data/logos/team_logos/Bundesliga.svg.png"
    bundesliga_logo_base64 = image_to_base64(bundesliga_logo_path)

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
            rotation=90,  # Start "Home Win" at the 12 o'clock position
            hole=0.4  # Create a donut chart
        )])

        # Add the Bundesliga logo in the center of the donut chart
        fig_predictions.add_layout_image(
            dict(
                source=f"data:image/png;base64,{bundesliga_logo_base64}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                sizex=0.2, sizey=0.2,
                xanchor="center", yanchor="middle",
                layer="above"
            )
        )

        # Update layout
        fig_predictions.update_layout(
            title_text="Group Predictions: Wins, Ties, Losses",
            height=500,
            width=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,  # Move legend below the pie chart
                xanchor="center",
                x=0.5,
                font=dict(size=12),  # Adjust font size for legend items
                itemwidth=30,  # Increase item width to allow all three labels in one row
            ),
            margin=dict(l=25, r=25, t=25, b=25)  # Equal margins for both charts
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
            rotation=90,  # Start "Home Win" at the 12 o'clock position
            hole=0.4  # Create a donut chart
        )])

        # Add the Bundesliga logo in the center of the donut chart
        fig_results.add_layout_image(
            dict(
                source=f"data:image/png;base64,{bundesliga_logo_base64}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                sizex=0.2, sizey=0.2,
                xanchor="center", yanchor="middle",
                layer="above"
            )
        )

        # Update layout
        fig_results.update_layout(
            title_text="Bundesliga Actual Results: Wins, Ties, Losses",
            height=500,
            width=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,  # Move legend below the pie chart
                xanchor="center",
                x=0.5,
                font=dict(size=12),  # Adjust font size for legend items
                itemwidth=30,  # Increase item width to allow all three labels in one row
            ),
            margin=dict(l=25, r=25, t=25, b=25)  # Equal margins for both charts
        )

        st.plotly_chart(fig_results)
