import streamlit as st
import pandas as pd
from PIL import Image
import base64
from io import BytesIO

# Utility function to load and convert image to base64
def load_image_as_base64(path):
    image = Image.open(path)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# Function to display the Overview section of the predictions page
def display_predictions_overview():
    st.subheader("Matchday Predictions - Overview")

    # Load the Bundesliga match preview data
    buli_df = pd.read_csv("data/buli_all_seasons.csv")

    # Filter for the 2023/24 season
    buli_df_2023 = buli_df[buli_df['Season'] == '2023/24']

    # Add matchday options with Matchday 34 as default (remove "--" as requested)
    matchday_options = list(buli_df_2023['Matchday'].unique()[::-1])

    # Dropdown to select matchday with 34 as the default
    selected_matchday = st.selectbox("Select Matchday", options=matchday_options, key="matchday_select_predictions_overview", index=0)

    # Store the selected matchday in session state
    st.session_state.selected_matchday = selected_matchday

    # Filter matches for the selected matchday
    filtered_matches = buli_df_2023[buli_df_2023["Matchday"] == selected_matchday]

    if filtered_matches.empty:
        st.error(f"No matches found for Matchday {selected_matchday}.")
        return
    
    # Convert 'Match Date' column to datetime for proper sorting and grouping
    filtered_matches['Match Date'] = pd.to_datetime(filtered_matches['Match Date'])

    # Sort the filtered matches by 'Match Date' and 'Match Time'
    filtered_matches = filtered_matches.sort_values(by=['Match Date', 'Match Time'])

    # Group matches by date and time
    grouped_matches = filtered_matches.groupby([filtered_matches['Match Date'], filtered_matches['Match Time']])

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
                if st.button("Details", key=f"{home_team}_details_{idx}"):
                    # Store the selected match and switch to Detail View tab
                    st.session_state.selected_match = f"{row['Home Tag']} - {row['Away Tag']}"
                    # Set the query parameter to switch to the Detail View
                    st.query_params.tab = "detail"

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