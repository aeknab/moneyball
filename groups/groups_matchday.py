import streamlit as st
import pandas as pd
from .utils import format_points, calculate_points

def display_matchday_section(matchday):
    st.subheader(f"Matchday {matchday} Overview")

    # Load and filter the merged_matchdays.csv file for the matchday section
    matchdays_df = pd.read_csv("data/merged_matchdays.csv")
    filtered_matches = matchdays_df[matchdays_df["Matchday"] == matchday]

    # Load the merged_rankings.csv file to get points for each player
    rankings_df = pd.read_csv("data/merged_rankings.csv")

    # Create the match names for the top row
    match_names = [f"{row['Home Team']} - {row['Away Team']}" for _, row in filtered_matches.iterrows()]

    # Initialize the data structure for the table
    table_data = {
        "Rank": ["", "Rank"] + list(range(1, 8)),
        "Name": ["", "Result"] + ["Andreas", "Gerd", "Geri", "Hermann", "Johnny", "Moddy", "Samson"]
    }

    # Add match columns with predictions and actual results
    for match_name in match_names:
        table_data[match_name] = [""]  # First row empty

        # Extract home and away teams from match_name
        home_team, away_team = match_name.split(" - ")

        # Get the actual results for the match
        home_goals_actual = filtered_matches.loc[
            (filtered_matches['Home Team'] == home_team) & (filtered_matches['Away Team'] == away_team), 
            'Home Goals'
        ].values[0]

        away_goals_actual = filtered_matches.loc[
            (filtered_matches['Home Team'] == home_team) & (filtered_matches['Away Team'] == away_team), 
            'Away Goals'
        ].values[0]

        # Append the actual results to the table_data
        table_data[match_name].append(f"{home_goals_actual}:{away_goals_actual}")

        # Loop through players and get their predictions
        for player in table_data["Name"][2:]:
            home_goals_pred = filtered_matches.loc[
                (filtered_matches['Home Team'] == home_team) & (filtered_matches['Away Team'] == away_team), 
                f"{player} Home Goals Predicted"
            ].values[0]

            away_goals_pred = filtered_matches.loc[
                (filtered_matches['Home Team'] == home_team) & (filtered_matches['Away Team'] == away_team), 
                f"{player} Away Goals Predicted"
            ].values[0]

            points = calculate_points(
                home_goals_pred, away_goals_pred, home_goals_actual, away_goals_actual
            )

            formatted_points = format_points(points)  # Apply color formatting
            prediction = f"{home_goals_pred}:{away_goals_pred} {formatted_points}"
            table_data[match_name].append(prediction)

    # Add points column
    table_data["Points"] = ["", "Points"] + [
        f"{int(rankings_df.loc[(rankings_df['Spieltag'] == matchday) & (rankings_df['Name'] == player), 'Punkte'].values[0])}"
        for player in table_data["Name"][2:]
    ]

    # Extract points as integers for sorting
    points_values = [int(point) for point in table_data["Points"][2:]]

    # Get sorted indices based on points (in descending order)
    sorted_indices = sorted(range(len(points_values)), key=lambda i: points_values[i], reverse=True)

    # Adjust sorted_indices to match the positions in table_data
    sorted_indices = [i + 2 for i in sorted_indices]  # Shift by 2 to account for headers

    # Include the first two rows (header and 'Result') in the sorted data
    sorted_indices = [0, 1] + sorted_indices

    # Rearrange table_data according to sorted_indices
    table_data = {k: [table_data[k][i] for i in sorted_indices] for k in table_data.keys()}

    # Update the Rank column to reflect the correct ranking (1 to 7)
    table_data["Rank"] = ["", "Rank"] + list(range(1, len(sorted_indices) - 1))

    # Construct the HTML table with styles
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
    .styled-table tbody tr {
        background-color: rgba(14, 17, 23, 0.35);
        border-bottom: 1px solid rgba(97, 101, 114, 0.9);
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

    # Add headers for matches
    for match_name in match_names:
        table_html += f"<th>{match_name}</th>"
    table_html += "<th></th></tr></thead><tbody>"  # Empty header for Points

    # Add the row for actual results
    table_html += "<tr><td>Rank</td><td>Name</td>"  # Rank and Name headers in the second row
    for match_name in match_names:
        table_html += f"<td>{table_data[match_name][1]}</td>"  # Actual match results
    table_html += "<td>Points</td></tr>"  # Points header in the second row

    # Add the rest of the rows
    for i in range(2, len(table_data["Rank"])):
        table_html += "<tr>"
        for col in table_data.keys():
            table_html += f"<td>{table_data[col][i]}</td>"
        table_html += "</tr>"

    table_html += "</tbody></table>"

    # Display the HTML table with st.markdown
    st.markdown(table_html, unsafe_allow_html=True)
