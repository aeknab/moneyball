import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os
import streamlit as st
from modules.utils import resize_image_to_bounding_box

def display_cross_table_view(df, selected_season, matchday):
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

    # Filter the dataset based on the selected season and matchday
    if selected_season == '2023/24':
        # For the 2023/24 season, exclude data from the selected matchday
        df_past_matches = df[(df['Matchday'] < matchday) & (df['Season'] == selected_season)]
    else:
        # For seasons 2005/06 to 2022/23, include data from the selected matchday
        df_past_matches = df[(df['Matchday'] <= matchday) & (df['Season'] == selected_season)]

    # Get the list of unique team tags for the selected season, limited to the teams that have played in that season
    teams_in_season = sorted(
        pd.unique(df_past_matches[['Home Tag', 'Away Tag']].values.ravel('K'))
    )

    # Reorder teams by their city names
    teams_in_season_sorted = sorted(teams_in_season, key=lambda tag: team_cities.get(tag, ''))

    # Create an empty DataFrame for the Kreuztabelle with teams ordered by city
    kreuztabelle = pd.DataFrame('--', index=teams_in_season_sorted, columns=teams_in_season_sorted)

    # Populate the Kreuztabelle with results
    for _, match in df_past_matches.iterrows():
        home_team = match['Home Tag']
        away_team = match['Away Tag']
        home_goals = match['Home Goals']
        away_goals = match['Away Goals']

        kreuztabelle.loc[home_team, away_team] = f"{home_goals}:{away_goals}"

    # Set diagonal cells to NaN for greyed out effect (teams don't play themselves)
    for team in teams_in_season_sorted:
        kreuztabelle.loc[team, team] = np.nan

    # Define colors and border colors
    colors = ['#a8e6a1', '#c4c4c4', 'lightyellow']
    border_colors = ['#388e3c', '#999999', '#FFD700']

    # Plot the Kreuztabelle
    fig, ax = plt.subplots(figsize=(12, 12))
    fig.patch.set_facecolor(mcolors.to_rgba((14/255, 17/255, 23/255, 0.35)))

    # Create the table with the grid
    ax.matshow(kreuztabelle.isnull(), cmap="gray_r", aspect='auto')
    ax.set_facecolor(mcolors.to_rgba((14/255, 17/255, 23/255, 0.35)))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # Ensure grid lines match the background color or remove them
    ax.grid(False)

    # Add text annotations for the scores and color the cells based on the outcome
    for i in range(len(kreuztabelle.index)):
        for j in range(len(kreuztabelle.columns)):
            value = kreuztabelle.iloc[i, j]
            if pd.notna(value) and value != '--':  # Ensure value is not '--'
                home_goals, away_goals = map(int, value.split(':'))
                if home_goals > away_goals:
                    color = colors[0]
                    border_color = border_colors[0]
                elif home_goals < away_goals:
                    color = colors[2]
                    border_color = border_colors[2]
                else:
                    color = colors[1]
                    border_color = border_colors[1]

                ax.add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, color=color, ec=border_color, lw=2))
                ax.text(j, i, value, ha='center', va='center', color="black")

    # Adjust plot limits to make space for logos
    ax.set_xlim(-1.5, len(kreuztabelle.columns) + 0.5)
    ax.set_ylim(len(kreuztabelle.index) + 0.5, -1.5)  # Invert y-axis

    def add_logo_at_position(ax, team_tag, x, y, box_alignment=(0.5, 0.5)):
        team_logo_path = f"data/logos/team_logos/{team_tag}.svg.png"
        if os.path.exists(team_logo_path):
            team_logo = Image.open(team_logo_path).convert("RGBA")  # Ensure the image is in RGBA format

            # Resize the image
            team_logo_resized = resize_image_to_bounding_box(team_logo, target_width=30, target_height=30)

            # Convert back to RGB to avoid transparency issues in matplotlib
            team_logo_resized = team_logo_resized.convert("RGB")

            # Add the logo to the plot
            logo = OffsetImage(np.array(team_logo_resized), zoom=1)
            ab = AnnotationBbox(logo, (x, y), frameon=False, box_alignment=box_alignment)
            ax.add_artist(ab)

    # Replace y-axis labels with logos
    for i, team_tag in enumerate(kreuztabelle.index):
        add_logo_at_position(ax, team_tag, -1, i)

    # Replace x-axis labels with logos
    for j, team_tag in enumerate(kreuztabelle.columns):
        add_logo_at_position(ax, team_tag, j, -1, box_alignment=(0.5, 0.5))  # Place logos at the bottom of the grid

    # Remove the default x and y labels
    ax.set_xticks([])
    ax.set_yticks([])

    # Display the chart
    st.pyplot(fig)
