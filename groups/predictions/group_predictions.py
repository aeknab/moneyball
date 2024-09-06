import streamlit as st
import pandas as pd
import base64
from PIL import Image
from io import BytesIO

# Utility function to load and convert image to base64
def load_image_as_base64(path):
    image = Image.open(path)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# Function to display the matchday predictions page
def display_predictions_page(user_id):
    st.subheader("Matchday Predictions")

    # Load and filter the merged_matchdays.csv file for the matchday section
    matchdays_df = pd.read_csv("data/merged_matchdays.csv")
    
    # Dropdown to select matchday
    matchday = st.selectbox("Select Matchday", options=list(range(1, 35))[::-1], key="matchday_select_predictions")

    # Add tabs for Overview and Detail view
    tab1, tab2 = st.tabs(["Overview", "Detail"])

    # Filter matches for the selected matchday
    filtered_matches = matchdays_df[matchdays_df["Matchday"] == matchday]

    if filtered_matches.empty:
        st.error(f"No matches found for Matchday {matchday}.")
        return

    # Display content based on selected tab
    with tab1:  # Overview
        st.write("Matches for the selected matchday:")
        for idx, row in filtered_matches.iterrows():
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

            # Adjust the columns to bring the "Details" button closer
            col1, col2, col3 = st.columns([3, 1.2, 2])

            with col1:
                st.markdown(f"""
                <div style='display: flex; align-items: center;'>
                    <div style='text-align: center;'>
                        <img src='data:image/png;base64,{home_logo_base64}' width='30'>
                    </div>
                    <div style='margin-left: 20px;'>
                        <span style='font-size: 20px; font-weight: bold;'>{home_team}</span>
                    </div>
                    <div style='text-align: center; margin: 0 15px;'>
                        <span style='font-weight:normal;'>vs.</span>
                    </div>
                    <div style='margin-right: 20px;'>
                        <span style='font-size: 20px; font-weight: bold;'>{away_team}</span>
                    </div>
                    <div style='text-align: center;'>
                        <img src='data:image/png;base64,{away_logo_base64}' width='30'>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # Add the "Details" button
                st.button("Details", key=f"{home_team}_details_{idx}")

            with col3:
                # Add home goals and away goals input fields in a row
                col_goals_home, col_separator, col_goals_away = st.columns([1, 0.2, 1])
                with col_goals_home:
                    home_goals = st.number_input(f"", min_value=0, max_value=10, key=f"{home_team}_goals_{idx}", label_visibility="collapsed", step=1, format="%d")
                with col_separator:
                    st.markdown("<span>:</span>", unsafe_allow_html=True)
                with col_goals_away:
                    away_goals = st.number_input(f"", min_value=0, max_value=10, key=f"{away_team}_goals_{idx}", label_visibility="collapsed", step=1, format="%d")

            # Add horizontal line to separate the matches
            st.markdown("<hr style='border: 1px solid #444;'>", unsafe_allow_html=True)

        # Add a "Save Predictions" button at the bottom
        if st.button("Save Predictions"):
            st.success("Predictions saved successfully!")

    with tab2:  # Detail
        st.write("Detailed match analysis will be displayed here.")