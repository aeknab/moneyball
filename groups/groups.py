import streamlit as st
import pandas as pd
from auth.database import fetch_all, execute_query
from groups.group_predictions import display_matchday_predictions
from ChatGPT.prompt_template import prompt_template
from openai import OpenAI

client = OpenAI(api_key="sk-o0hrLU1sy_khDaVw-sFP1pnIOP-SLylV1lC-gaOgLWT3BlbkFJ7b2I0vPST6fT6vgTB90vaf-DIDxpOg00Z8ax3cOhIA")

def format_points(points):
    """Formats points with color based on the score."""
    if points == 0:
        return f"<span style='color:grey'>({points})</span>"
    elif points == 2:
        return f"<span style='color:yellow'>({points})</span>"
    elif points == 3:
        return f"<span style='color:orange'>({points})</span>"
    elif points == 4:
        return f"<span style='color:red'>({points})</span>"
    return f"({points})"

def display_groups_page():
    st.title("My Groups")

    # Fetch the user's groups from the database
    groups = fetch_all('''
        SELECT g.*, ug.is_admin 
        FROM groups g 
        JOIN user_groups ug ON g.id = ug.group_id 
        WHERE ug.user_id = ?
    ''', (st.session_state['user_id'],))

    if groups:
        # Group Selection with Radio Buttons
        selected_group_name = st.radio("Select a Group", [group['name'] for group in groups])

        # Find the selected group data
        selected_group = next(group for group in groups if group['name'] == selected_group_name)
        is_admin = selected_group['is_admin']

        st.write(f"Group Name: {selected_group['name']}")
        st.write(f"Description: {selected_group['description']}")

        if is_admin:
            if st.button("Delete Group"):
                execute_query('DELETE FROM groups WHERE id = ?', (selected_group['id'],))
                execute_query('DELETE FROM user_groups WHERE group_id = ?', (selected_group['id'],))
                st.success("Group deleted successfully!")
                st.experimental_rerun()

        # Section Selection (Overview, Matchday, Predictions, Summary)
        section = st.radio("Section", ["Overview", "Matchday", "Predictions", "Summary"])

        # Matchday Dropdown - Most recent matchday on top
        matchday = st.selectbox("Select Matchday", options=list(range(1, 35))[::-1])

        # Load the merged_rankings.csv file for both Overview and Matchday sections
        rankings_df = pd.read_csv("data/merged_rankings.csv")

        # Load and filter the merged_matchdays.csv file
        matchdays_df = pd.read_csv("data/merged_matchdays.csv")

        if section == "Overview":
            st.subheader(f"Group Overview for Matchday {matchday}")

            # Filter by the selected matchday
            filtered_df = rankings_df[rankings_df["Spieltag"] == matchday]

            # Sort by Rank
            sorted_df = filtered_df.sort_values(by="Rang")

            # Select relevant columns and rename them for display
            overview_data = sorted_df[["Rang", "Name", "Punkte", "Gesamtpunkte"]]
            overview_data.columns = ["Rank", "Name", "Matchday Points", "Total Points"]

            # Display the table without the "Matchdays" column and remove the first column
            st.table(overview_data.set_index("Rank"))

        elif section == "Matchday":
            st.subheader(f"Matchday {matchday} Overview")

            # Filter by the selected matchday
            filtered_matches = matchdays_df[matchdays_df["Matchday"] == matchday]

            # Create the match names for the top row
            match_names = [f"{row['Home Team']} - {row['Away Team']}" for _, row in filtered_matches.iterrows()]

            # Initialize the data structure for the table
            table_data = {
                "Rank": ["", "Rank"] + list(range(1, 8)),
                "Name": ["", "Result"] + ["Andreas", "Gerd", "Geri", "Hermann", "Johnny", "Moddy", "Samson"]
            }

            # Add match columns with predictions
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
            table_data["Points"] = ["", "Points"] + [f"{int(rankings_df.loc[(rankings_df['Spieltag'] == matchday) & (rankings_df['Name'] == player), 'Punkte'].values[0])}" for player in table_data["Name"][2:]]

            # Extract points as integers for sorting
            points_values = [int(point) for point in table_data["Points"][2:]]

            # Get sorted indices based on points (in descending order)
            sorted_indices = sorted(range(len(points_values)), key=lambda i: points_values[i], reverse=True)

            # Adjust sorted_indices to match the positions in `table_data`
            sorted_indices = [i + 2 for i in sorted_indices]  # Shift by 2 to account for headers

            # Include the first two rows (header and 'Result') in the sorted data
            sorted_indices = [0, 1] + sorted_indices

            # Rearrange table_data according to sorted_indices
            table_data = {k: [table_data[k][i] for i in sorted_indices] for k in table_data.keys()}

            # Update the `Rank` column to reflect the correct ranking (1 to 7)
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

        elif section == "Predictions":
            st.subheader(f"Enter Predictions for Matchday {matchday}")

            # Get user ID from session
            user_id = st.session_state['user_id']

            # Display and save predictions for each match
            display_matchday_predictions("2023/24", matchday, user_id)

            # Display the user's predictions
            st.subheader("Your Predictions")
            predictions = fetch_all(
                'SELECT * FROM predictions WHERE user_id = ? AND match_id IN (SELECT id FROM matches WHERE matchday = ? AND season = ?)', 
                (user_id, matchday, "2023/24")
            )
            if predictions:
                for prediction in predictions:
                    st.write(f"Match ID: {prediction['match_id']}, Home Goals: {prediction['home_goals']}, Away Goals: {prediction['away_goals']}")
            else:
                st.write("No predictions found.")
                
        elif section == "Summary":
            st.subheader(f"Matchday {matchday} Summary")

            # Filter by the selected matchday
            filtered_matches = matchdays_df[matchdays_df["Matchday"] == matchday]

            # Ensure that filtered_matches and sorted_df are populated
            filtered_df = rankings_df[rankings_df["Spieltag"] == matchday]
            sorted_df = filtered_df.sort_values(by="Rang")

            if not filtered_matches.empty and not sorted_df.empty:
                # Generate the matchday summary
                matchday_summary = generate_summary(filtered_matches, selected_group_name, sorted_df, matchday, len(groups))

                # Display the generated summary
                if matchday_summary:
                    st.write(matchday_summary)
                else:
                    st.write("No summary could be generated.")
            else:
                st.write("No data available for this matchday.")

def calculate_points(pred_home, pred_away, actual_home, actual_away):
    """Calculates points based on prediction and actual results."""
    pred_diff = pred_home - pred_away
    actual_diff = actual_home - actual_away

    if pred_home == actual_home and pred_away == actual_away:
        return 4  # Exact score
    elif pred_diff == actual_diff:
        if pred_diff == 0:  # Both predicted and actual results are ties but with different scores
            return 2
        return 3  # Correct goal difference
    elif (pred_home > pred_away and actual_home > actual_away) or (pred_home < pred_away and actual_home < actual_away):
        return 2  # Correct outcome/tendency
    else:
        return 0  # Wrong prediction

def generate_summary(filtered_matches, selected_group_name, sorted_df, matchday, group_size):
    """Generates a summary using OpenAI API."""

    # Prepare the match results and player scores
    match_results = "\n".join([f"{row['Home Team']} {row['Home Goals']}:{row['Away Goals']} {row['Away Team']}" for _, row in filtered_matches.iterrows()])
    player_scores = "\n".join([f"{row['Rang']}. {row['Name']} - {row['Gesamtpunkte']} points" for _, row in sorted_df.iterrows()])

    # Fill in the prompt with the dynamic data
    prompt = prompt_template.format(
        group_size=group_size,
        matchday=matchday,
        match_results=match_results,
        player_scores=player_scores
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred while generating the summary: {e}"
