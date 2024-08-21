# groups/group_predictions.py

import streamlit as st
from auth.database import fetch_all, execute_query

# Function to get matches for a specific matchday and season
def get_matches_for_matchday(season, matchday):
    query = 'SELECT id, home_team, away_team FROM matches WHERE season = ? AND matchday = ?'
    matches = fetch_all(query, (season, matchday))
    return matches

# Function to save a user's prediction for a match
def save_prediction(user_id, match_id, home_goals, away_goals):
    query = '''
        INSERT INTO predictions (user_id, match_id, home_goals, away_goals)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, match_id) DO UPDATE SET
        home_goals = excluded.home_goals,
        away_goals = excluded.away_goals,
        updated_at = CURRENT_TIMESTAMP
    '''
    execute_query(query, (user_id, match_id, home_goals, away_goals))

# Function to display the prediction input fields for a specific match
def display_prediction_input(user_id, match_id, home_team, away_team):
    st.subheader(f"{home_team} vs {away_team}")

    # Create input fields for predicting the score
    home_goals = st.number_input(f"{home_team} Goals", min_value=0, max_value=10, value=0)
    away_goals = st.number_input(f"{away_team} Goals", min_value=0, max_value=10, value=0)

    if st.button(f"Save Prediction for {home_team} vs {away_team}"):
        save_prediction(user_id, match_id, home_goals, away_goals)
        st.success("Prediction saved!")

# Example function to display all matches for a matchday and allow predictions
def display_matchday_predictions(season, matchday, user_id):
    matches = get_matches_for_matchday(season, matchday)
    if matches:
        for match in matches:
            display_prediction_input(user_id, match['id'], match['home_team'], match['away_team'])
    else:
        st.write("No matches found for this matchday.")
