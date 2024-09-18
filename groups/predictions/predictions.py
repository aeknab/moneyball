import streamlit as st
from groups.predictions.overview.predictions_overview import display_predictions_overview
from groups.predictions.detail.predictions_detail import display_predictions_detail

def display_predictions_page():
    # Get the current URL query parameters
    query_params = st.query_params.to_dict()

    # Check if the "tab" parameter is set to "detail"
    if "tab" in query_params and query_params["tab"] == "detail":
        # Display the Detail View tab
        tab1, tab2 = st.tabs(["Overview", "Match View"])
        with tab2:
            display_predictions_detail()  # Show the Detail View tab
        with tab1:
            display_predictions_overview()
    else:
        # Default to Overview tab
        tab1, tab2 = st.tabs(["Overview", "Match View"])
        with tab1:
            display_predictions_overview()  # Display the Overview tab
        with tab2:
            display_predictions_detail()  # Display the Detail View tab