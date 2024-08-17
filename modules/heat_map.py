import streamlit as st
import pandas as pd
import plotly.express as px

def plot_heat_map(df, color_codes_df):
    # This is where the code for generating the heat map will go
    st.write("Heat Map - Under Construction")

def display_heat_map(df, selected_season, matchday, color_codes_df):
    st.header("Heat Map")
    df_filtered = df[(df['Season'] == selected_season) & (df['Matchday'] <= matchday)]
    
    plot_heat_map(df_filtered, color_codes_df)
