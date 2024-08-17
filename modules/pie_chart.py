import streamlit as st
import pandas as pd
import plotly.express as px

def plot_pie_chart(df, color_codes_df):
    # This is where the code for generating the pie chart will go
    st.write("Pie Chart - Under Construction")

def display_pie_chart(df, selected_season, matchday, color_codes_df):
    st.header("Pie Chart")
    df_filtered = df[(df['Season'] == selected_season) & (df['Matchday'] <= matchday)]
    
    plot_pie_chart(df_filtered, color_codes_df)
