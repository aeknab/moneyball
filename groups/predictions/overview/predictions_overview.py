import streamlit as st
import pandas as pd
import base64
from PIL import Image
from io import BytesIO
from bundesliga.utils import resize_image, load_image

# Utility function to load and convert image to base64
def load_image_as_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# Function to save predictions (placeholder)
def save_predictions(predictions):
    # Implement your saving logic here
    pass  # Placeholder

# Function to display the Overview section of the predictions page
def display_predictions_overview():
    # Load the Bundesliga match preview data
    buli_df = pd.read_csv("data/buli_all_seasons.csv")

    # Filter for the 2023/24 season
    buli_df_2023 = buli_df[buli_df['Season'] == '2023/24']

    # Add matchday options with the latest matchday as default
    matchday_options = list(buli_df_2023['Matchday'].unique()[::-1])

    # Dropdown to select matchday with the latest matchday as default
    selected_matchday = st.selectbox(
        "Select Matchday",
        options=matchday_options,
        key="matchday_select_predictions_overview",
        index=0
    )

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
    grouped_matches = filtered_matches.groupby(
        [filtered_matches['Match Date'], filtered_matches['Match Time']]
    )

    # Initialize a list to store predictions
    predictions = []

    # Get the colors from Streamlit theme to match input fields
    input_background_color = st.get_option("theme.secondaryBackgroundColor") or "#262730"
    input_text_color = st.get_option("theme.textColor") or "#FAFAFA"

    # Iterate over each grouped date and time
    for (match_date, match_time), matches in grouped_matches:
        # Format date and time for display
        match_date_str = match_date.strftime('%A, %d %B %Y')
        match_time_str = pd.to_datetime(match_time).strftime('%H:%M')

        # Combine date and time into a single line
        header_str = f"{match_date_str} @ {match_time_str}"

        # Display the date and time with styling for the box with rounded edges
        st.markdown(f"""
        <div style="background-color: {input_background_color}; border-radius: 10px; padding: 10px; margin: 10px 0; display: inline-block;">
            <span style="font-size: 16px; font-weight: bold; color: {input_text_color};">{header_str}</span>
        </div>
        """, unsafe_allow_html=True)

        # Now display the matches for this specific date and time
        for idx, row in matches.iterrows():
            home_team = row['Home Team']
            away_team = row['Away Team']
            home_tag = row['Home Tag']
            away_tag = row['Away Tag']
            home_logo_path = f"data/logos/team_logos/{home_tag}.svg.png"
            away_logo_path = f"data/logos/team_logos/{away_tag}.svg.png"

            # Load and resize the logos
            home_logo = load_image(home_logo_path)
            away_logo = load_image(away_logo_path)
            target_area = 10000  # Adjust this value to control the overall size
            home_logo_resized = resize_image(home_logo, target_area)
            away_logo_resized = resize_image(away_logo, target_area)

            home_logo_base64 = load_image_as_base64(home_logo_resized)
            away_logo_base64 = load_image_as_base64(away_logo_resized)

            # Adjust the layout: Stack logos and team names on top of each other
            col1, col2, col3 = st.columns([3, 1.2, 2])

            with col1:
                st.markdown(f"""
                <div style='display: flex; align-items: center;'>
                    <div style='text-align: center;'>
                        <img src='data:image/png;base64,{home_logo_base64}' width='25' style='display:block;'>
                        <img src='data:image/png;base64,{away_logo_base64}' width='25' style='display:block; margin-top: 20px;'>  <!-- Increased margin -->
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
                    st.session_state.selected_match = f"{home_tag} - {away_tag}"
                    # Set the query parameter to switch to the Detail View
                    st.query_params = {"tab": "detail"}
                    st.rerun()  # Switch to the Match View tab

            with col3:
                # Add home goals and away goals input fields in a row
                col_goals_home, col_separator, col_goals_away = st.columns([1, 0.2, 1])
                with col_goals_home:
                    home_goals = st.number_input(
                        f"",
                        min_value=0,
                        max_value=10,
                        key=f"{home_team}_goals_{idx}",
                        label_visibility="collapsed",
                        step=1,
                        format="%d"
                    )
                with col_separator:
                    st.markdown("<span>:</span>", unsafe_allow_html=True)
                with col_goals_away:
                    away_goals = st.number_input(
                        f"",
                        min_value=0,
                        max_value=10,
                        key=f"{away_team}_goals_{idx}",
                        label_visibility="collapsed",
                        step=1,
                        format="%d"
                    )

            # Store the prediction
            predictions.append({
                'match_id': idx,
                'home_team': home_team,
                'away_team': away_team,
                'home_goals': home_goals,
                'away_goals': away_goals
            })

            # Add horizontal line to separate matches
            st.markdown("<hr style='border: 0.5px solid #444;'>", unsafe_allow_html=True)

    # Add "Submit Predictions" button at the bottom
    col1, col2, col3 = st.columns([6.5, 6.5, 4])

    with col3:
        submit_button = st.button("Submit Predictions", key="submit_predictions_button")
        if submit_button:
            st.success("Button clicked!")  # Placeholder action