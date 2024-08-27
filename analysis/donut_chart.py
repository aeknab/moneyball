import streamlit as st
import plotly.graph_objs as go
import pandas as pd
from PIL import Image
from groups.utils import calculate_points, image_to_base64

# Define the new color palette with 75% transparency for the chart
colors = ['rgba(196, 196, 196, 0.85)',  # Grey with 75% transparency
          'rgba(255, 250, 205, 0.85)',  # Light yellow with 75% transparency
          'rgba(135, 206, 235, 0.85)',  # Light blue with 75% transparency
          'rgba(168, 230, 161, 0.85)']  # Light green with 75% transparency

border_colors = ['rgba(153, 153, 153, 1)',  # Dark grey (solid)
                 'rgba(255, 215, 0, 1)',    # Gold (solid)
                 'rgba(70, 130, 180, 1)',   # Steel blue (solid)
                 'rgba(56, 142, 60, 1)']    # Dark green (solid)

def display_donut_chart(matchdays_df, selected_players, matchday):
    st.subheader("Donut Chart")

    # Initialize a dictionary to count occurrences of each outcome and their contribution to total points
    outcome_counts = {
        '0 Points': 0,
        '2 Points': 0,
        '3 Points': 0,
        '4 Points': 0
    }
    total_points_contribution = {
        '0 Points': 0,
        '2 Points': 0,
        '3 Points': 0,
        '4 Points': 0
    }

    total_predictions = 0
    total_points = 0

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
            total_points += points

            if points == 0:
                outcome_counts['0 Points'] += 1
                total_points_contribution['0 Points'] += points
            elif points == 2:
                outcome_counts['2 Points'] += 1
                total_points_contribution['2 Points'] += points
            elif points == 3:
                outcome_counts['3 Points'] += 1
                total_points_contribution['3 Points'] += points
            elif points == 4:
                outcome_counts['4 Points'] += 1
                total_points_contribution['4 Points'] += points

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
        hovertemplate='<b>%{label}:</b> %{customdata[0]} of ' + f'{total_points} Points<extra></extra>',
        customdata=[[total_points_contribution['0 Points']],
                    [total_points_contribution['2 Points']],
                    [total_points_contribution['3 Points']],
                    [total_points_contribution['4 Points']]],
        sort=False,  # Explicitly do not sort slices by size
        direction='clockwise',  # Ensure sections are placed in a clockwise order
        rotation=90  # Start "0 Points" at the 12 o'clock position
    )])

    # Add a circular background in the center of the donut chart
    fig.add_shape(
        type="circle",
        xref="paper", yref="paper",
        x0=0.35, y0=0.35, x1=0.65, y1=0.65,
        line=dict(color="rgba(14, 17, 23, 0)"),  # No border
        fillcolor="rgba(14, 17, 23, 0.35)",
        layer="below"  # Make sure it is below the logo
    )

    # Load the Bundesliga logo
    bundesliga_logo_path = "data/logos/team_logos/Bundesliga.svg.png"
    bundesliga_logo = Image.open(bundesliga_logo_path)
    logo_base64 = image_to_base64(bundesliga_logo)

    # Add the Bundesliga logo in the center of the donut chart
    fig.add_layout_image(
        dict(
            source=f"data:image/png;base64,{logo_base64}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=0.2, sizey=0.2,
            xanchor="center", yanchor="middle",
            layer="above"  # Ensure it's above the background circle
        )
    )

    # Update layout to move legend and adjust margins
    fig.update_layout(
        title_text=f"Prediction Accuracy for {' and '.join(selected_players)} up to Matchday {matchday}",
        height=600,
        width=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.3,  # Move legend closer to the chart
            xanchor="center",
            x=0.5,
            font=dict(size=10),  # Adjust font size for legend items
            itemwidth=30,  # Adjust the width allocated for each item
        ),
        margin=dict(l=20, r=20, t=20, b=20)  # Adjust margins to prevent cropping
    )

    # Display the donut chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
