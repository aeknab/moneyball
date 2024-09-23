import streamlit as st
from groups.predictions.overview.predictions_overview import display_predictions_overview
from groups.predictions.detail.predictions_detail import display_predictions_detail

def display_predictions_page():
    # Get the current URL query parameters using st.query_params
    query_params = st.query_params  # Fetch query params using the new method

    # Check if the "tab" parameter is set to "detail"
    if "tab" in query_params and query_params["tab"] == "detail":
        # Display the Detail View tab if the query param is set
        tab1, tab2 = st.tabs(["Overview", "Match View"])
        with tab2:
            display_predictions_detail()  # Show the Detail View tab content
        with tab1:
            display_predictions_overview()  # Show the Overview tab content
    else:
        # Default to Overview tab
        tab1, tab2 = st.tabs(["Overview", "Match View"])
        with tab1:
            display_predictions_overview()  # Display the Overview tab content
        with tab2:
            display_predictions_detail()  # Display the Detail View tab content