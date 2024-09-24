import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from PIL import Image
import base64
from analysis.utils import generate_analysis
from ChatGPT.prompt_pie_chart import pie_chart_prompt_template

def image_to_base64(img_path):
    """Convert image to base64 string."""
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def calculate_pie_chart_data(matchdays_df, selected_players):
    """Calculate the data used for the pie charts."""
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

    return predictions, results

def display_group_pie_chart(matchdays_df, selected_players):
    st.subheader("Pie Charts")

    # Calculate the data for the pie charts
    predictions, results = calculate_pie_chart_data(matchdays_df, selected_players)

    # Define the colors with 85% transparency
    colors = ['rgba(168, 230, 161, 0.85)', 'rgba(196, 196, 196, 0.85)', 'rgba(255, 250, 205, 0.85)']
    border_colors = ['rgba(56, 142, 60, 1)', 'rgba(153, 153, 153, 1)', 'rgba(255, 215, 0, 1)']

    # Determine which image to use based on the selected player(s)
    if len(selected_players) == 1 and selected_players[0] != 'All':
        player_logo_path = f"data/logos/groups/{selected_players[0]}.png"
        player_logo_size = 0.55  # Larger size for individual players
    else:
        player_logo_path = "data/logos/groups/just_the_tipp.png"
        player_logo_size = 0.35  # Standard size for the group logo

    player_logo_base64 = image_to_base64(player_logo_path)

    # Load the Bundesliga logo for the right chart
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

        # Add the player's logo (or the default group logo) in the center of the donut chart
        fig_predictions.add_layout_image(
            dict(
                source=f"data:image/png;base64,{player_logo_base64}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                sizex=player_logo_size,  # Adjust the size of the player image
                sizey=player_logo_size,  # Adjust the size of the player image
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
                sizex=0.5,  # Standard size for the Bundesliga logo
                sizey=0.5,  # Standard size for the Bundesliga logo
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

def generate_pie_chart_analysis(selected_players, matchdays_df):
    # Calculate the data for pie charts
    predictions, results = calculate_pie_chart_data(matchdays_df, selected_players)

    try:
        # Calculate percentages
        win_percentage = (predictions['Home Win'] / sum(predictions.values())) * 100
        draw_percentage = (predictions['Tie'] / sum(predictions.values())) * 100
        lose_percentage = (predictions['Away Win'] / sum(predictions.values())) * 100

        results_win_percentage = (results['Home Win'] / sum(results.values())) * 100
        actual_draw_percentage = (results['Tie'] / sum(results.values())) * 100
        results_lose_percentage = (results['Away Win'] / sum(results.values())) * 100

        # Use the first selected player as the player_name
        player_name = selected_players[0] if len(selected_players) == 1 else "All Players"

    except (KeyError, TypeError, ValueError) as e:
        st.error(f"An error occurred while accessing data: {e}")
        return None

    # Example prompt with data-driven feedback
    prompt = pie_chart_prompt_template.format(
        player_name=player_name,
        win_percentage=win_percentage,
        draw_percentage=draw_percentage,
        lose_percentage=lose_percentage,
        user_draw_percentage=draw_percentage,
        actual_draw_percentage=actual_draw_percentage,
        results_win_percentage=results_win_percentage,
        results_lose_percentage=results_lose_percentage
    )

    return generate_analysis(prompt)