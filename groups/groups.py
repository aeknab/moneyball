import streamlit as st
import pandas as pd
from auth.database import fetch_all
from groups.group_predictions import display_matchday_predictions

def display_groups_page():
    st.title("My Groups")

    # Fetch the user's groups from the database
    groups = fetch_all('''
        SELECT g.* 
        FROM groups g 
        JOIN user_groups ug ON g.id = ug.group_id 
        WHERE ug.user_id = ?
    ''', (st.session_state['user_id'],))

    if groups:
        # Group Selection with Radio Buttons
        selected_group_name = st.radio("Select a Group", [group['name'] for group in groups])

        # Find the selected group data
        selected_group = next(group for group in groups if group['name'] == selected_group_name)

        st.write(f"Group Name: {selected_group['name']}")
        st.write(f"Description: {selected_group['description']}")

        # Section Selection (Overview, Matchday, Predictions)
        section = st.radio("Section", ["Overview", "Matchday", "Predictions"])

        # Matchday Dropdown - Most recent matchday on top
        matchday = st.selectbox("Select Matchday", options=list(range(1, 35))[::-1])

        # Load the merged_rankings.csv file for both Overview and Matchday sections
        rankings_df = pd.read_csv("data/merged_rankings.csv")

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

            # Load and filter the merged_matchdays.csv file
            matchdays_df = pd.read_csv("data/merged_matchdays.csv")

            # Filter by the selected matchday
            filtered_matches = matchdays_df[matchdays_df["Matchday"] == matchday]

            # Create the match names for the top row
            match_names = [f"{row['Home Team']} - {row['Away Team']}" for _, row in filtered_matches.iterrows()]

            # Initialize the data structure for the table
            matchday_data = {
                "": ["Result", "Andreas", "Gerd", "Geri", "Hermann", "Johnny", "Moddy", "Samson"],
            }

            # Add match columns with predictions
            for match_name in match_names:
                matchday_data[match_name] = []

            # Add the actual match results first in each match column
            for _, match_row in filtered_matches.iterrows():
                matchday_data[f"{match_row['Home Team']} - {match_row['Away Team']}"].append(
                    f"**{match_row['Home Goals']} - {match_row['Away Goals']}**"
                )

            # Fill in predictions for each player
            for player in matchday_data[""][1:]:  # Skip "Result" row
                for _, match_row in filtered_matches.iterrows():
                    home_goals = match_row[f"{player} Home Goals Predicted"]
                    away_goals = match_row[f"{player} Away Goals Predicted"]
                    matchday_data[f"{match_row['Home Team']} - {match_row['Away Team']}"].append(f"{home_goals}-{away_goals}")

            # Filter and load points from rankings_df
            points_df = rankings_df[(rankings_df["Spieltag"] == matchday) & (rankings_df["Name"].isin(matchday_data[""][1:]))]
            points_dict = dict(zip(points_df["Name"], points_df["Punkte"]))

            # Calculate the sum of points for all players for the "Result" row
            total_points_sum = sum(points_dict.values())

            # Add points to the table and sort by points
            matchday_data["Points"] = [f"**{total_points_sum}**"] + [f"**{points_dict.get(player, 0)}**" for player in matchday_data[""][1:]]

            # Ensure all columns have the same length
            max_length = max(len(col) for col in matchday_data.values())
            for key in matchday_data:
                while len(matchday_data[key]) < max_length:
                    matchday_data[key].append("")

            # Create DataFrame and display
            matchday_df = pd.DataFrame(matchday_data)
            matchday_df["Points"] = pd.to_numeric(matchday_df["Points"].str.replace("**", "", regex=False), errors='coerce').fillna(0).astype(int)
            matchday_df = matchday_df.sort_values(by="Points", ascending=False)

            st.table(matchday_df)

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
    else:
        st.write("You are not part of any groups yet.")
