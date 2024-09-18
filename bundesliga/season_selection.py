# season_selection.py

import streamlit as st
import pandas as pd

def select_season_match_fixture(df):
    # Layout for filters: Place them side by side
    col1, col2, col3 = st.columns(3)

    # Dropdown for Season
    with col1:
        seasons = ['--'] + sorted(df['Season'].unique(), reverse=True)
        selected_season = st.selectbox("Season", seasons)

    # Dropdown for Matchday
    with col2:
        if selected_season != '--':
            df_season = df[df['Season'] == selected_season]
            matchdays = ['--'] + sorted(df_season['Matchday'].unique(), reverse=True)
        else:
            matchdays = ['--']
        selected_matchday = st.selectbox("Matchday", matchdays)

    # Dropdown for Fixture
    with col3:
        if selected_matchday != '--':
            df_matches = df_season[df_season['Matchday'] == selected_matchday]
            match_options = ['--'] + df_matches.apply(
                lambda row: f"{row['Home Tag']} vs. {row['Away Tag']}", axis=1).tolist()
        else:
            match_options = ['--']
            df_matches = pd.DataFrame()

        selected_match = st.selectbox("Fixture", match_options)

    if selected_season == '--' or selected_matchday == '--' or selected_match == '--':
        return selected_season, selected_matchday, selected_match, None

    return selected_season, selected_matchday, selected_match, df_matches