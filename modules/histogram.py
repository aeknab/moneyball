import streamlit as st
import pandas as pd
import plotly.express as px

def plot_histogram(df, color_codes_df):
    # This is where the code for generating the histogram will go
    st.write("Histogram - Under Construction")

def display_histogram(df, selected_season, matchday, color_codes_df):
    st.header("Histogram")
    df_filtered = df[(df['Season'] == selected_season) & (df['Matchday'] <= matchday)]
    
    plot_histogram(df_filtered, color_codes_df)
