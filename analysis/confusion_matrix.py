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

    # Calculate total predictions for percentage calculation
    total_predictions = confusion_matrix.values.sum()

    # Create the heatmap using Plotly with transparency
    fig = go.Figure(data=go.Heatmap(
        z=confusion_matrix.values,
        x=confusion_matrix.columns,
        y=confusion_matrix.index,
        colorscale='Viridis',  # Use Viridis color scale
        zmin=0,
        zmax=confusion_matrix.values.max(),
        opacity=0.85,  # Set the transparency to 85%
        showscale=False  # Hide the color scale bar
    ))

    # Add borders to each cell by adding shapes
    for i in range(3):
        for j in range(3):
            fig.add_shape(
                type="rect",
                x0=j-0.5, y0=i-0.5, x1=j+0.5, y1=i+0.5,
                line=dict(color="rgba(0, 0, 0, 0.85)", width=2)  # 85% transparency on the borders
            )

            # Calculate the percentage for the current cell
            percentage = (confusion_matrix.iloc[i, j] / total_predictions) * 100

            # Add annotations (percentages) to each cell
            fig.add_annotation(
                x=j, y=i,
                text=f"{percentage:.1f}%",  # Format the percentage to 1 decimal place
                showarrow=False,
                font=dict(color="white", size=12),
                xanchor='center',
                yanchor='middle'
            )

    # Update layout
    fig.update_layout(
        title_text=f"Confusion Matrix for {' and '.join(selected_players)} (Up to Matchday {matchday})",
        xaxis_title='Actual Outcome',
        yaxis_title='Predicted Outcome',
        xaxis=dict(tickmode='array', tickvals=['Home Win', 'Tie', 'Away Win']),
        yaxis=dict(
            tickmode='array', 
            tickvals=['Home Win', 'Tie', 'Away Win'],
            tickangle=-90  # Rotate y-axis labels 90 degrees
        ),
        height=600,
        width=600,
        showlegend=False
    )

    # Display the confusion matrix in Streamlit
    st.plotly_chart(fig, use_container_width=True)

