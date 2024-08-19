import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from PIL import Image
from modules.utils import image_to_base64

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
        labels=list(results.keys()),
        values=list(results.values()),
        hole=.4,  # Makes it a donut chart
        marker=dict(colors=colors, line=dict(color=border_colors, width=2)),
        textinfo='percent',  # Only show percentages in bold
        textfont=dict(size=18, color='black', family='Arial', weight='bold'),  # Bold font
        hoverinfo='label+value+text',  # Show the number of events and the total
        texttemplate='%{percent:.1%}',  # Format the percentage
        hovertemplate='%{label}:<br>%{value}/' + str(total_matches) + '<extra></extra>',  # Custom hover text
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

    # Add the Bundesliga logo in the center of the donut chart
    fig.add_layout_image(
        dict(
            source=f"data:image/png;base64,{logo_base64}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=0.2, sizey=0.2,
            xanchor="center", yanchor="middle",
            layer="above"  # Ensure it's above the background circle
        )
    )

    # Update layout
    fig.update_layout(
        title_text=f"Bundesliga Results Leading Up to Matchday {selected_matchday}",
        height=600,
        width=600,
        showlegend=True,
    )

    # Display the pie chart
    st.plotly_chart(fig)

def plot_pie_chart_animation(df, selected_season, max_matchday):
    st.subheader("Bundesliga Results Pie Chart Animation")
    
    frames = []
    colors = ['#a8e6a1', '#c4c4c4', 'lightyellow']
    border_colors = ['#388e3c', '#999999', '#FFD700']

    for day in range(1, max_matchday + 1):  # Ensure animation includes all matchdays up to the selected one
        df_filtered = filter_matches_for_season(df, selected_season, day)

        # Aggregate results for each matchday
        results = {
            'Home Win': df_filtered['Result'][df_filtered['Result'] == 'Home Win'].count(),
            'Tie': df_filtered['Result'][df_filtered['Result'] == 'Tie'].count(),
            'Away Win': df_filtered['Result'][df_filtered['Result'] == 'Away Win'].count()
        }

        total_matches = sum(results.values())

        # Create a frame for each matchday
        frames.append(go.Frame(
            data=[go.Pie(
                labels=list(results.keys()),
                values=list(results.values()),
                hole=.4,
                marker=dict(colors=colors, line=dict(color=border_colors, width=2)),
                textinfo='percent',
                textfont=dict(size=18, color='black', family='Arial', weight='bold'),
                hoverinfo='label+value+text',
                texttemplate='%{percent:.1%}',
                hovertemplate='%{label}:<br>%{value}/' + str(total_matches) + '<extra></extra>',
            )],
            name=f"Matchday {day}"
        ))

    fig = go.Figure(
        data=frames[0].data,
        frames=frames,
        layout=go.Layout(
            updatemenus=[dict(type="buttons",
                              showactive=False,
                              buttons=[dict(label="Play",
                                            method="animate",
                                            args=[None, {"frame": {"duration": 500, "redraw": True},
                                                         "fromcurrent": True, "mode": "immediate"}]),
                                       dict(label="Pause",
                                            method="animate",
                                            args=[[None], {"frame": {"duration": 0, "redraw": False},
                                                           "mode": "immediate"}])],
                              direction="left",
                              x=0.1, xanchor="left", y=-0.15, yanchor="top")],
            sliders=[{
                'steps': [{'args': [[f"Matchday {i}"], {'frame': {'duration': 500, 'redraw': True},
                                                     'mode': 'immediate'}],
                           'label': f"{i}",
                           'method': 'animate'} for i in range(1, max_matchday + 1)],  # Include up to the selected matchday
                'x': 0.3, 'len': 0.65,
                'currentvalue': {'prefix': 'Matchday: ', 'font': {'size': 15}, 'visible': True, 'offset': -30},
            }]
        )
    )

    # Add a circular background in the center of the donut chart
    fig.add_shape(
        type="circle",
        xref="paper", yref="paper",
        x0=0.35, y0=0.35, x1=0.65, y1=0.65,
        line=dict(color="rgba(14, 17, 23, 0)"),  # No border
        fillcolor="rgba(14, 17, 23, 0.35)",
        layer="below"
    )

    # Add the Bundesliga logo in the center of the donut chart
    bundesliga_logo_path = "data/logos/team_logos/Bundesliga.svg.png"
    bundesliga_logo = Image.open(bundesliga_logo_path)
    logo_base64 = image_to_base64(bundesliga_logo)

    fig.add_layout_image(
        dict(
            source=f"data:image/png;base64,{logo_base64}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=0.2, sizey=0.2,
            xanchor="center", yanchor="middle",
            layer="above"
        )
    )

    fig.update_layout(
        title_text="Bundesliga Results Pie Chart Animation",
        height=600,
        width=600,
        showlegend=True,
    )

    st.plotly_chart(fig)

def display_pie_chart_with_animation(df, selected_season, selected_matchday):
    # Plot the static pie chart
    display_pie_chart(df, selected_season, selected_matchday)

    # Add the play animation button
    if st.button("Play Animation", key="piechart_animation"):
        plot_pie_chart_animation(df[df['Season'] == selected_season], selected_season, selected_matchday)
