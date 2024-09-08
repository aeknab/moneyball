import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from PIL import Image
from bundesliga.utils import image_to_base64

# Function to filter matches based on the selected season and matchday
def filter_matches_for_season(df, selected_season, matchday):
    if selected_season == '2023/24':
        # Exclude data from the selected matchday for the 2023/24 season
        return df[(df['Season'] == selected_season) & (df['Matchday'] < matchday)]
    else:
        # Include data from the selected matchday for previous seasons (2005/06 to 2022/23)
        return df[(df['Season'] == selected_season) & (df['Matchday'] <= matchday)]

def display_pie_chart(df, selected_season, selected_matchday):
    st.subheader("Bundesliga Results Pie Chart")

    # Filter the data using the updated filtering function
    df_filtered = filter_matches_for_season(df, selected_season, selected_matchday)

    # Aggregate actual Bundesliga results
    results = {
        'Home Win': df_filtered['Result'][df_filtered['Result'] == 'Home Win'].count(),
        'Tie': df_filtered['Result'][df_filtered['Result'] == 'Tie'].count(),
        'Away Win': df_filtered['Result'][df_filtered['Result'] == 'Away Win'].count()
    }

    # Define the colors for the pie chart
    colors = ['#a8e6a1', '#c4c4c4', 'lightyellow']
    border_colors = ['#388e3c', '#999999', '#FFD700']  # Using gold color for away win border

    # Calculate the total number of matches
    total_matches = sum(results.values())

    # Create the pie chart using Plotly
    fig = go.Figure(data=[go.Pie(
        labels=['Home Win', 'Tie', 'Away Win'],  # Explicit order: Wins first, then ties, then losses
        values=[results['Home Win'], results['Tie'], results['Away Win']],  # Corresponding values in order
        hole=.4,  # Adjusted to make the donut ring thicker
        marker=dict(colors=colors, line=dict(color=border_colors, width=2)),
        textinfo='percent',
        textfont=dict(size=18, color='black', family='Arial', weight='bold'),
        hoverinfo='label+value+text',
        texttemplate='%{percent:.1%}',
        hovertemplate='%{label}:<br>%{value}/' + str(total_matches) + '<extra></extra>',
        sort=False,  # Explicitly do not sort slices by size
        direction='clockwise',  # Ensure sections are placed in a clockwise order
        rotation=90  # Start "Home Win" at the 12 o'clock position
    )])

    # Add a circular background in the center of the donut chart
    fig.add_shape(
        type="circle",
        xref="paper", yref="paper",
        x0=0.35, y0=0.35, x1=0.65, y1=0.65,
        line=dict(color="rgba(14, 17, 23, 0)"),  # No border
        fillcolor="rgba(14, 17, 23, 0.35)",
        layer="below"  # Make sure it is below the logo
    )

    # Load the Bundesliga logo
    bundesliga_logo_path = "data/logos/team_logos/Bundesliga.svg.png"
    bundesliga_logo = Image.open(bundesliga_logo_path)
    logo_base64 = image_to_base64(bundesliga_logo)

    # Increase the size of the Bundesliga logo in the center of the donut chart
    fig.add_layout_image(
        dict(
            source=f"data:image/png;base64,{logo_base64}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=0.35,  # Increase sizex
            sizey=0.35,  # Increase sizey
            xanchor="center", yanchor="middle",
            layer="above"  # Ensure it's above the background circle
        )
    )

    # Update layout to place the legend under the chart
    fig.update_layout(
        title_text=f"Bundesliga Results Leading Up to Matchday {selected_matchday}",
        height=700,  # Increase height to accommodate the legend
        width=600,
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="top",
            y=-0.2,  # Position the legend below the chart
            xanchor="center",
            x=0.5
        )
    )

    # Display the pie chart
    st.plotly_chart(fig)