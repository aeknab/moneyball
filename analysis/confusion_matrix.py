import streamlit as st
import plotly.graph_objs as go
import numpy as np
import pandas as pd

def display_confusion_matrix(matchdays_df, selected_players, matchday):
    st.subheader("Confusion Matrix")

    # Filter the data up to the selected matchday
    filtered_df = matchdays_df[matchdays_df['Matchday'] <= matchday]

    # Initialize confusion matrix
    confusion_matrix = pd.DataFrame(
        np.zeros((3, 3), dtype=int),
        columns=['Home Win', 'Tie', 'Away Win'],
        index=['Home Win', 'Tie', 'Away Win']
    )

    # Populate confusion matrix
    for player in selected_players:
        pred_col = f'{player} Result Predicted'
        actual_col = 'Result'

        for pred, actual in zip(filtered_df[pred_col], filtered_df[actual_col]):
            confusion_matrix.loc[pred, actual] += 1

    # Create the heatmap using Plotly
    fig = go.Figure(data=go.Heatmap(
        z=confusion_matrix.values,
        x=confusion_matrix.columns,
        y=confusion_matrix.index,
        colorscale='Viridis',  # Use Viridis color scale
        colorbar=dict(title='Counts'),
        zmin=0
    ))

    # Update layout
    fig.update_layout(
        title_text=f"Confusion Matrix for {' and '.join(selected_players)} (Up to Matchday {matchday})",
        xaxis_title='Actual Outcome',
        yaxis_title='Predicted Outcome',
        xaxis=dict(tickmode='array', tickvals=['Home Win', 'Tie', 'Away Win']),
        yaxis=dict(tickmode='array', tickvals=['Home Win', 'Tie', 'Away Win']),
        height=600,
        width=600,
        showlegend=False
    )

    # Display the confusion matrix in Streamlit
    st.plotly_chart(fig, use_container_width=True)
