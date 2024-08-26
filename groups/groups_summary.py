import streamlit as st
import pandas as pd
from ChatGPT.summaries import generate_summary

def display_summaries_section(matchday, selected_group_name, rankings_df, matchdays_df):
    st.subheader(f"Matchday {matchday} Summary")

    # Filter by the selected matchday
    filtered_matches = matchdays_df[matchdays_df["Matchday"] == matchday]

    # Ensure that filtered_matches and sorted_df are populated
    filtered_df = rankings_df[rankings_df["Spieltag"] == matchday]
    sorted_df = filtered_df.sort_values(by="Rang")

    if not filtered_matches.empty and not sorted_df.empty:
        # Generate the matchday summary
        matchday_summary = generate_summary(filtered_matches, selected_group_name, sorted_df)

        # Display the generated summary
        if matchday_summary:
            st.write(matchday_summary)
        else:
            st.write("No summary could be generated.")
    else:
        st.write("No data available for this matchday.")
