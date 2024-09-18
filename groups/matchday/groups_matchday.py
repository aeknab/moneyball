import streamlit as st
import pandas as pd
import base64
from PIL import Image
from io import BytesIO
from ..utils import format_points, calculate_points
from ChatGPT.summaries import generate_summary

def load_image_as_base64(path):
    image = Image.open(path)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def display_matchday_section(matchday):

    # Load and filter the merged_matchdays.csv file for the matchday section
    matchdays_df = pd.read_csv("data/merged_matchdays.csv")
    filtered_matches = matchdays_df[matchdays_df["Matchday"] == matchday]

    if filtered_matches.empty:
        st.error(f"No matches found for Matchday {matchday}.")
        return

    # Load the merged_rankings.csv file to get points for each player
    rankings_df = pd.read_csv("data/merged_rankings.csv")

    # Create the match names for the top row with logos
    match_names = []
    for _, row in filtered_matches.iterrows():
        home_team = row['Home Team']
        away_team = row['Away Team']

        home_logo_path = f"data/logos/team_logos/{home_team}.svg.png"
        away_logo_path = f"data/logos/team_logos/{away_team}.svg.png"

        try:
            home_logo_base64 = load_image_as_base64(home_logo_path)
            away_logo_base64 = load_image_as_base64(away_logo_path)
        except FileNotFoundError:
            st.error(f"Logo not found for {home_team} or {away_team}.")
            continue

        match_name = f"<img src='data:image/png;base64,{home_logo_base64}' width='20'> <span style='font-weight:normal;'>vs.</span> <img src='data:image/png;base64,{away_logo_base64}' width='20'>"
        match_names.append(match_name)

    # Initialize the data structure for the table
    table_data = {
        "Rank": ["", "<b>Rank</b>"] + list(range(1, 8)),
        "Name": ["", "<b>Name</b>"] + ["Andreas", "Gerd", "Geri", "Hermann", "Johnny", "Moddy", "Samson"]
    }

    # Add match columns with predictions and actual results
    for match_name, (_, row) in zip(match_names, filtered_matches.iterrows()):
        table_data[match_name] = [""]  # First row empty

        home_team_tag = row['Home Team']
        away_team_tag = row['Away Team']

        # Get the actual results for the match
        home_goals_actual = row['Home Goals']
        away_goals_actual = row['Away Goals']

        # Check if actual goals data is found
        if pd.isna(home_goals_actual) or pd.isna(away_goals_actual):
            st.error(f"No actual results found for {home_team_tag} vs. {away_team_tag}.")
            continue

        # Append the actual results to the table_data
        table_data[match_name].append(f"{home_goals_actual}:{away_goals_actual}")

        # Loop through players and get their predictions
        for player in table_data["Name"][2:]:
            home_goals_pred = row[f"{player} Home Goals Predicted"]
            away_goals_pred = row[f"{player} Away Goals Predicted"]

            # Check if predicted goals data is found
            if pd.isna(home_goals_pred) or pd.isna(away_goals_pred):
                st.error(f"No predictions found for {player} for the match {home_team_tag} vs. {away_team_tag}.")
                table_data[match_name].append("N/A")  # Append 'N/A' if predictions are missing
                continue

            points = calculate_points(
                home_goals_pred, away_goals_pred, home_goals_actual, away_goals_actual
            )

            formatted_points = format_points(points)  # Apply color formatting
            prediction = f"{home_goals_pred}:{away_goals_pred} {formatted_points}"
            table_data[match_name].append(prediction)

    # Add points column
    table_data["Points"] = ["", "<b>Points</b>"] + [
        f"<b>{int(rankings_df.loc[(rankings_df['Spieltag'] == matchday) & (rankings_df['Name'] == player), 'Punkte'].values[0])}</b>"
        for player in table_data["Name"][2:]
    ]

    # Add player faces to the left of their names, with adjusted size and alignment
    for i in range(2, len(table_data["Name"])):
        player_name = table_data["Name"][i].strip("<b>").strip("</b>")
        player_logo_path = f"data/logos/groups/{player_name}.png"
        try:
            player_logo = Image.open(player_logo_path)
            player_logo_base64 = load_image_as_base64(player_logo_path)
            table_data["Name"][i] = f"<img src='data:image/png;base64,{player_logo_base64}' width='50' style='vertical-align:middle;'> <b>{player_name}</b>"
        except FileNotFoundError:
            st.error(f"Logo not found for player {player_name}")
            table_data["Name"][i] = f"<b>{player_name}</b>"

    # Extract points as integers for sorting, stripping out any HTML tags
    points_values = []
    for point in table_data["Points"][2:]:
        clean_point = int(point.replace('<b>', '').replace('</b>', ''))
        points_values.append(clean_point)

    # Get sorted indices based on points (in descending order)
    sorted_indices = sorted(range(len(points_values)), key=lambda i: points_values[i], reverse=True)

    # Adjust sorted_indices to match the positions in table_data
    sorted_indices = [i + 2 for i in sorted_indices]  # Shift by 2 to account for headers

    # Include the first two rows (header and 'Result') in the sorted data
    sorted_indices = [0, 1] + sorted_indices

    # Rearrange table_data according to sorted_indices
    table_data = {k: [table_data[k][i] for i in sorted_indices] for k in table_data.keys()}

    # Update the Rank column to reflect the correct ranking (1 to 7)
    table_data["Rank"] = ["", "<b>Rank</b>"] + list(range(1, len(sorted_indices) - 1))

    # Construct the HTML table with styles, adjusting column widths and adding the thick line
    table_html = """
    <style>
    .styled-table {
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        font-family: 'Sans-serif', Arial, Helvetica, sans-serif;
        width: 100%;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
        border-radius: 15px;
        overflow: hidden;
        background-color: rgba(255, 255, 255, 0.5);
        border: 2px solid #696969;
    }
    .styled-table thead tr {
        background-color: rgba(14, 17, 23, 0.70);
        color: #ffffff;
        text-align: left;
    }
    .styled-table th,
    .styled-table td {
        padding: 12px 15px;
        text-align: center;
    }
    .styled-table th:nth-child(2),
    .styled-table td:nth-child(2) {
        width: 200px; /* Adjusted width for Name column */
    }
    .styled-table th:nth-child(1),
    .styled-table td:nth-child(1),
    .styled-table th:last-child,
    .styled-table td:last-child {
        width: 50px; /* Narrower width for Rank and Points columns */
    }
    .styled-table tbody tr {
        background-color: rgba(14, 17, 23, 0.35);
        border-bottom: 1px solid rgba(97, 101, 114, 0.9);
    }
    .styled-table tbody tr:first-of-type {
        background-color: rgba(14, 17, 23, 0.525); /* Adjust transparency for Rank/Name/Points row */
        border-bottom: 2px solid #696969; /* Thick line for the Rank/Name/Points row */
    }
    .styled-table tbody tr:last-of-type {
        border-bottom: 2px solid rgba(97, 101, 114, 0.9);
    }
    </style>
    <table class="styled-table">
    <thead>
        <tr>
            <th></th> <!-- Empty header for Rank -->
            <th></th> <!-- Empty header for Name -->
    """

    # Add headers for matches with bold tags
    for match_name in match_names:
        table_html += f"<th><b>{match_name}</b></th>"
    table_html += "<th></th></tr></thead><tbody>"  # Empty header for Points

    # Add the row for actual results with bold tags and thick line underneath
    table_html += "<tr style='border-bottom: 3px solid #696969;'><td><b>Rank</b></td><td><b>Name</b></td>"  # Rank and Name headers in the second row
    for match_name in match_names:
        table_html += f"<td><b>{table_data[match_name][1]}</b></td>"  # Actual match results in bold
    table_html += "<td><b>Points</b></td></tr>"  # Points header in the second row

    # Add the rest of the rows
    for i in range(2, len(table_data["Rank"])):
        table_html += "<tr>"
        for col in table_data.keys():
            table_html += f"<td>{table_data[col][i]}</td>"
        table_html += "</tr>"

    table_html += "</tbody></table>"

    # Display the HTML table with st.markdown
    st.markdown(table_html, unsafe_allow_html=True)

    # Add a button for generating the Matchday Summary
    if st.button("Matchday Summary"):
        # Generate and display the matchday summary
        summary = generate_summary(filtered_matches, "Test Group", rankings_df)
        st.markdown(summary)