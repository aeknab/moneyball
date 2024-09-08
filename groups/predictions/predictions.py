import streamlit as st
from groups.predictions.overview.predictions_overview import display_predictions_overview
from groups.predictions.detail.predictions_detail import display_predictions_detail

def display_predictions_page():
    st.title("Predictions Page")

    # Add tabs for Overview and Detail View
    tab1, tab2 = st.tabs(["Overview", "Detail View"])

    with tab1:
        display_predictions_overview()  # Display the Overview tab

    with tab2:
        display_predictions_detail()  # Display the Detail View tab