import streamlit as st
import pandas as pd
from analysis.group_table import display_group_table
from analysis.bump_chart_group import display_group_bump_chart

def display_overview_section(matchday, rankings_df):
    st.subheader(f"Group Overview for Matchday {matchday}")

    # Load the merged_rankings.csv file for the overview section
    # (This is redundant now since rankings_df is already passed, but kept for reference)
    # rankings_df = pd.read_csv("data/merged_rankings.csv")

    # Filter by the selected matchday
    filtered_df = rankings_df[rankings_df["Spieltag"] == matchday]

    # Sort by Rank
    sorted_df = filtered_df.sort_values(by="Rang")

    # Add a column for the rank change (+/-) compared to the previous matchday
    if matchday > 1:
        # Get the previous matchday data
        previous_matchday = matchday - 1
        previous_df = rankings_df[rankings_df["Spieltag"] == previous_matchday]
        
        # Merge current and previous matchday data on the player name
        merged_df = pd.merge(
            sorted_df[['Name', 'Rang']],
            previous_df[['Name', 'Rang']],
            on='Name',
            suffixes=('', '_previous'),
            how='left'
        )

        # Calculate the rank change
        merged_df['Rank Change'] = merged_df.apply(
            lambda row: '⬆️' if row['Rang'] < row['Rang_previous'] else ('⬇️' if row['Rang'] > row['Rang_previous'] else '⏺️'),
            axis=1
        )

        # Add the rank change to the sorted_df
        sorted_df = pd.merge(sorted_df, merged_df[['Name', 'Rank Change']], on='Name', how='left')
    else:
        # For Matchday 1, set the rank change to "--"
        sorted_df['Rank Change'] = '--'

    # Add MD Winner column (Spieltagssieger)
    sorted_df['MD Winner'] = sorted_df['Spieltagssieger'].apply(
        lambda x: f"🏆{x:.1f}" if x > 0 and x < 1 else ('🏆' if x == 1 else '')
    )

    # Add MD Wins column (Gesamtspieltagssiege) without the trophy emoji
    sorted_df['MD Wins'] = sorted_df['Gesamtspieltagssiege'].apply(
        lambda x: f"x {x}" if x > 0 else ''
    )

    # Determine if it's the last matchday (34) and assign medals
    if matchday == 34:
        sorted_df['Total Points'] = sorted_df.apply(
            lambda row: f"🥇 {row['Gesamtpunkte']}" if row['Rang'] == 1 else (
                        f"🥈 {row['Gesamtpunkte']}" if row['Rang'] == 2 else (
                        f"🥉 {row['Gesamtpunkte']}" if row['Rang'] == 3 else str(row['Gesamtpunkte']))),
            axis=1
        )
    else:
        sorted_df['Total Points'] = sorted_df['Gesamtpunkte']

    # Select relevant columns and rename them for display
    overview_data = sorted_df[["Rang", "Rank Change", "Name", "Punkte", "MD Winner", "MD Wins", "Total Points"]]
    overview_data.columns = ["Rank", "+/-", "Name", "Matchday Points", "MD Winner", "MD Wins", "Total Points"]

    # Construct the HTML table with styles for the Overview section
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
            <th>Rank</th>
            <th>+/-</th>
            <th>Name</th>
            <th>Matchday Points</th>
            <th>MD Winner</th>
            <th>MD Wins</th>
            <th>Total Points</th>
        </tr>
    </thead>
    <tbody>
    """

    # Add rows from overview_data
    for _, row in overview_data.iterrows():
        table_html += f"<tr><td>{row['Rank']}</td><td>{row['+/-']}</td><td>{row['Name']}</td><td>{row['Matchday Points']}</td><td>{row['MD Winner']}</td><td>{row['MD Wins']}</td><td>{row['Total Points']}</td></tr>"

    table_html += "</tbody></table>"

    # Display the HTML table with st.markdown
    st.markdown(table_html, unsafe_allow_html=True)

    # Display the Group Table below the overview
    display_group_table(matchday, rankings_df, selected_players=sorted_df['Name'].tolist())

    # Display the Bump Chart below the table
    display_group_bump_chart(matchday, rankings_df, selected_players=sorted_df['Name'].tolist())
