import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os
import streamlit as st
from groups.utils import resize_image_to_bounding_box, calculate_points, format_points  # Ensure correct imports

# Mapping of team tags to cities
team_cities = {
    'B04': 'Leverkusen',
    'BMG': 'Mönchengladbach',
    'BVB': 'Dortmund',
    'FCB': 'München',
    'FCA': 'Augsburg',
    'SCF': 'Freiburg',
    'KOE': 'Köln',
    'M05': 'Mainz',
    'RBL': 'Leipzig',
    'SGE': 'Frankfurt',
    'VFB': 'Stuttgart',
    'SVW': 'Bremen',
    'WOB': 'Wolfsburg',
    'FCU': 'Berlin',
    'BOC': 'Bochum',
    'HDH': 'Heidenheim',
    'D98': 'Darmstadt',
    'TSG': 'Hoffenheim',
    'MSV': 'Duisburg',
    'HSV': 'Hamburg',
    'H96': 'Hannover',
    'S04': 'Gelsenkirchen',
    'BSC': 'Berlin',
    'FCK': 'Kaiserslautern',
    'FCN': 'Nürnberg',
    'DSC': 'Bielefeld',
    'FCE': 'Cottbus',
    'ALE': 'Aachen',
    'KSC': 'Karlsruhe',
    'FCH': 'Rostock',
    'STP': 'St. Pauli',
    'SGF': 'Fürth',
    'F95': 'Düsseldorf',
    'EBS': 'Braunschweig',
    'SCP': 'Paderborn',
    'FCI': 'Ingolstadt',
    'KIE': 'Kiel'
}

def display_player_crosstable_view(df_past_predictions, selected_player, matchday):
    # Add this line to inspect the columns
    print(df_past_predictions.columns)

    # Get the list of unique teams involved, using the city mapping for ordering
    teams_in_season = sorted(pd.unique(df_past_predictions[['Home Team', 'Away Team']].values.ravel('K')), key=lambda x: team_cities.get(x, x))

    # Create an empty DataFrame for the crosstable with teams ordered by cities alphabetically
    crosstable = pd.DataFrame('--', index=teams_in_season, columns=teams_in_season)

    # Populate the crosstable with predictions and actual results
    for _, match in df_past_predictions.iterrows():
        home_team = match['Home Team']
        away_team = match['Away Team']

        # Player's predictions
        home_goals_pred = match[f"{selected_player} Home Goals Predicted"]
        away_goals_pred = match[f"{selected_player} Away Goals Predicted"]

        # Actual match results
        home_goals_actual = match['Home Goals']
        away_goals_actual = match['Away Goals']

        # Calculate points based on the player's predictions
        points = calculate_points(home_goals_pred, away_goals_pred, home_goals_actual, away_goals_actual)
        
        # Format the prediction with the points
        formatted_prediction = f"{home_goals_pred}:{away_goals_pred} {format_points(points)}"
        
        # Insert into the crosstable
        crosstable.loc[home_team, away_team] = formatted_prediction

    # Set diagonal cells to NaN for greyed out effect (teams don't play themselves)
    for team in teams_in_season:
        crosstable.loc[team, team] = np.nan

    # Define colors and border colors based on points
    colors = ['#a8e6a1', '#c4c4c4', 'lightyellow', '#84a6de']  # 4 points, 3 points, 2 points, 0 points
    border_colors = ['#388e3c', '#999999', '#FFD700', '#00274c']  # Border colors corresponding to points

    # Plot the crosstable
    fig, ax = plt.subplots(figsize=(12, 12))
    fig.patch.set_facecolor(mcolors.to_rgba((14/255, 17/255, 23/255, 0.35)))

    # Create the table with the grid
    ax.matshow(crosstable.isnull(), cmap="gray_r", aspect='auto')
    ax.set_facecolor(mcolors.to_rgba((14/255, 17/255, 23/255, 0.35)))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # Ensure grid lines match the background color or remove them
    ax.grid(False)

    # Add text annotations for the predictions and color the cells based on the points
    for i in range(len(crosstable.index)):
        for j in range(len(crosstable.columns)):
            value = crosstable.iloc[i, j]
            if pd.notna(value) and value != '--':  # Ensure value is not '--'
                # Extract the points from the formatted string
                points = int(value.split()[1][1])  # Assuming points are always in the format (X)

                if points == 4:
                    color = colors[0]
                    border_color = border_colors[0]
                elif points == 3:
                    color = colors[1]
                    border_color = border_colors[1]
                elif points == 2:
                    color = colors[2]
                    border_color = border_colors[2]
                else:
                    color = colors[3]
                    border_color = border_colors[3]

                ax.add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, color=color, ec=border_color, lw=2))
                ax.text(j, i, value, ha='center', va='center', color="black", fontsize=10)

    # Adjust plot limits to make space for logos
    ax.set_xlim(-1.5, len(crosstable.columns) + 0.5)
    ax.set_ylim(len(crosstable.index) + 0.5, -1.5)  # Invert y-axis

    def add_logo_at_position(ax, team_tag, x, y, box_alignment=(0.5, 0.5)):
        team_logo_path = f"data/logos/groups/{team_tag}.png"
        if os.path.exists(team_logo_path):
            team_logo = Image.open(team_logo_path).convert("RGBA")  # Ensure the image is in RGBA format

            # Resize the image
            team_logo_resized = resize_image_to_bounding_box(team_logo, target_width=50, target_height=50)

            # Keep the image in RGBA to preserve transparency
            # Add the logo to the plot
            logo = OffsetImage(np.array(team_logo_resized), zoom=0.5)  # Adjust zoom to ensure sharpness
            ab = AnnotationBbox(logo, (x, y), frameon=False, box_alignment=box_alignment)
            ax.add_artist(ab)

    # Replace y-axis labels with logos
    for i, team_tag in enumerate(crosstable.index):
        add_logo_at_position(ax, team_tag, -1, i)

    # Replace x-axis labels with logos
    for j, team_tag in enumerate(crosstable.columns):
        add_logo_at_position(ax, team_tag, j, -1, box_alignment=(0.5, 0.5))  # Place logos at the bottom of the grid

    # Remove the default x and y labels
    ax.set_xticks([])
    ax.set_yticks([])

    # Display the chart
    st.pyplot(fig)