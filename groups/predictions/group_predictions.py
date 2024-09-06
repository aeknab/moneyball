import streamlit as st
import pandas as pd
from PIL import Image
import base64
from io import BytesIO
from bundesliga.match_preview import display_match_preview

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

    # Load the Bundesliga match preview data
    buli_df = pd.read_csv("data/buli_all_seasons.csv")

    # Filter for the 2023/24 season
    buli_df_2023 = buli_df[buli_df['Season'] == '2023/24']

    # Dropdown to select matchday
    matchday = st.selectbox("Select Matchday", options=buli_df_2023['Matchday'].unique()[::-1], key="matchday_select_predictions")

    # Filter matches for the selected matchday
    filtered_matches = buli_df_2023[buli_df_2023["Matchday"] == matchday]

    if filtered_matches.empty:
        st.error(f"No matches found for Matchday {matchday}.")
        return

    # Convert 'Match Date' column to datetime for proper sorting and grouping
    filtered_matches['Match Date'] = pd.to_datetime(filtered_matches['Match Date'])

    # Sort the filtered matches by 'Match Date' and 'Match Time'
    filtered_matches = filtered_matches.sort_values(by=['Match Date', 'Match Time'])

    # Group matches by date and then by time
    grouped_matches = filtered_matches.groupby([filtered_matches['Match Date'], filtered_matches['Match Time']])

    # Add tabs for Overview and Detailed View
    tab1, tab2 = st.tabs(["Overview", "Detail View"])

    with tab1:
        st.write("Overview Tab")
        
        # Iterate over each grouped date and time
        for (match_date, match_time), matches in grouped_matches:
            # Format date and time for display
            match_date_str = match_date.strftime('%A, %d %B %Y')
            match_time_str = pd.to_datetime(match_time).strftime('%H:%M')
            
            # Combine date and time into a single line
            header_str = f"{match_date_str} @ {match_time_str}"

            # Display the date and time with styling for the box with rounded edges
            st.markdown(f"""
            <div style="background-color: #2E2E2E; border-radius: 10px; padding: 10px; margin: 10px 0; display: inline-block;">
                <span style="font-size: 16px; font-weight: bold; color: #E0E0E0;">{header_str}</span>
            </div>
            """, unsafe_allow_html=True)

            # Now display the matches for this specific date and time
            for idx, row in matches.iterrows():
                home_team = row['Home Team']
                away_team = row['Away Team']
                home_logo_path = f"data/logos/team_logos/{row['Home Tag']}.svg.png"
                away_logo_path = f"data/logos/team_logos/{row['Away Tag']}.svg.png"

                try:
                    home_logo_base64 = load_image_as_base64(home_logo_path)
                    away_logo_base64 = load_image_as_base64(away_logo_path)
                except FileNotFoundError:
                    st.error(f"Logo not found for {home_team} or {away_team}.")
                    continue

                # Adjust the layout: Stack logos and team names on top of each other
                col1, col2, col3 = st.columns([3, 1.2, 2])

                with col1:
                    st.markdown(f"""
                    <div style='display: flex; align-items: center;'>
                        <div style='text-align: center;'>
                            <img src='data:image/png;base64,{home_logo_base64}' width='25' style='display:block;'>
                            <img src='data:image/png;base64,{away_logo_base64}' width='25' style='display:block; margin-top: 5px;'>
                        </div>
                        <div style='margin-left: 15px;'>
                            <span style='font-size: 16px;'>{home_team} <br> <span style='font-weight: normal; color: grey;'>vs.</span> <br> {away_team}</span>
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

                # Add horizontal line to separate matches
                st.markdown("<hr style='border: 0.5px solid #444;'>", unsafe_allow_html=True)

    with tab2:
        st.write("Detail Tab")
        for idx, row in filtered_matches.iterrows():
            match_label = f"{row['Home Team']} vs. {row['Away Team']}"

            if st.button(f"Show Details for {match_label}", key=f"details_{idx}_detail"):
                # Display match preview for this fixture
                display_match_preview(buli_df_2023[buli_df_2023["Matchday"] == matchday])  # Pass the filtered DataFrame for previews

    # Add a "Save Predictions" button at the bottom
    if st.button("Save Predictions"):
        st.success("Predictions saved successfully!")