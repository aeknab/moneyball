import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from PIL import Image
from bundesliga.utils import get_team_colors, load_image, resize_image, image_to_base64

# Function to filter matches based on the selected season and matchday
def filter_matches_for_season(df, selected_season, matchday):
    if selected_season == '2023/24':
        # Exclude data from the selected matchday for the 2023/24 season
        return df[(df['Season'] == selected_season) & (df['Matchday'] < matchday)]
    else:
        # Include data from the selected matchday for previous seasons (2005/06 to 2022/23)
        return df[(df['Season'] == selected_season) & (df['Matchday'] <= matchday)]

def resize_image(image, target_width):
    width_percent = target_width / float(image.size[0])
    target_height = int(float(image.size[1]) * float(width_percent))
    return image.resize((target_width, target_height), Image.LANCZOS)

def plot_bump_chart(df, color_codes_df, selected_season, matchday):
    # Ensure matchday 34 is included for past seasons
    df_season_before_matchday = filter_matches_for_season(df, selected_season, matchday)
    
    if not df_season_before_matchday.empty:
        # Initialize a DataFrame to hold the rankings for each matchday
        rankings = []
    
        # Iterate through each matchday up to the selected matchday
        for md in range(1, matchday + 1):  # Include the selected matchday
            df_md = df_season_before_matchday[df_season_before_matchday['Matchday'] == md]
    
            # Collect the ranks for both the home and away teams
            for index, row in df_md.iterrows():
                rankings.append({
                    'Team Tag': row['Home Tag'], 
                    'Rank': row['Home Team Rank'], 
                    'Matchday': md,
                    'Opponent': row['Away Tag'],
                    'Location': 'H',
                    'Score': f"{row['Home Goals']}:{row['Away Goals']}"
                })
                rankings.append({
                    'Team Tag': row['Away Tag'], 
                    'Rank': row['Away Team Rank'], 
                    'Matchday': md,
                    'Opponent': row['Home Tag'],
                    'Location': 'A',
                    'Score': f"{row['Away Goals']}:{row['Home Goals']}"
                })
    
        # Convert the rankings list to a DataFrame
        df_rankings = pd.DataFrame(rankings)
    
        # Pivot the data to have matchdays as columns and teams as rows
        df_bump = df_rankings.pivot(index='Team Tag', columns='Matchday', values='Rank')
    
        # Plot the bump chart using Plotly
        fig = go.Figure()

        # Iterate through each team and plot their rank over the matchdays
        for team_tag in df_bump.index:
            primary_color, _ = get_team_colors(team_tag, color_codes_df)
            if primary_color.lower() == '#000000' or primary_color.lower() == 'black':
                primary_color = '#FFFFFF'  # Use white color for better visibility

            team_data = df_rankings[df_rankings['Team Tag'] == team_tag]
            hover_texts = [
                f"vs. {row['Opponent']} ({row['Location']})<br>{row['Score']}"
                for _, row in team_data.iterrows()
            ]
            fig.add_trace(go.Scatter(
                x=df_bump.columns,
                y=df_bump.loc[team_tag],
                mode='lines+markers',
                marker=dict(size=8, color=primary_color),
                line=dict(width=3, color=primary_color),
                name=team_tag,
                text=hover_texts,  # Custom hover text
                hoverinfo='text'
            ))

            # Add team logos at the end of the line
            team_logo_path = f"data/logos/team_logos/{team_tag}.svg.png"
            team_logo = load_image(team_logo_path)
            team_logo_resized = resize_image(team_logo, target_width=30)
            logo_base64 = image_to_base64(team_logo_resized)

            # Get the last matchday position for the logo placement
            end_x = df_bump.columns[-1]
            end_y = df_bump.loc[team_tag].iloc[-1]
            fig.add_layout_image(
                dict(
                    source=f'data:image/png;base64,{logo_base64}',
                    xref="x", yref="y",
                    x=end_x + 0.4,  # Move logos slightly to the right
                    y=end_y,
                    sizex=1.5,  # Adjust the size of the logos
                    sizey=1.5,
                    xanchor="left",
                    yanchor="middle"
                )
            )
    
        # Customize the chart
        fig.update_layout(
            title=f'Bundesliga Bump Chart: League Position by Matchday ({selected_season})',
            xaxis=dict(
                title='Matchday', 
                tickmode='linear', 
                tick0=1, 
                dtick=1, 
                range=[0.5, 34.9],  # Extra space on the right
                showgrid=True,
                tickvals=list(range(1, 35)),  # Show Matchdays 1-34
                ticktext=list(range(1, 35)),  # Ensure all matchdays are shown
            ),
            yaxis=dict(
                title='Rank', 
                autorange='reversed', 
                tickvals=list(range(1, 19)), 
                range=[0.5, 18.5],  # Adjusted range to reduce space
                showgrid=True
            ),
            plot_bgcolor='rgba(14, 17, 23, 0.70)',  # Transparent background color
            paper_bgcolor='rgba(0,0,0,0)',
            height=800,
            width=1000,
            showlegend=False,
        )

        # Add vertical grid line at the halfway mark (between 17th and 18th matchday)
        fig.add_vline(x=17.5, line=dict(color='rgba(255, 255, 255, 0.5)', dash='dot', width=1.5))  # White dotted line with 50% transparency
    
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No data available for bump chart.")

def animate_bump_chart(df, color_codes_df, selected_season, selected_matchday):
    # Prepare the data for animation
    df_season = filter_matches_for_season(df, selected_season, selected_matchday)
    rankings = []

    for md in range(1, selected_matchday + 1):  # Include the selected matchday in the animation
        df_md = df_season[df_season['Matchday'] == md]
        for index, row in df_md.iterrows():
            rankings.append({
                'Team Tag': row['Home Tag'], 
                'Rank': row['Home Team Rank'], 
                'Matchday': md,
                'Opponent': row['Away Tag'],
                'Location': 'H',
                'Score': f"{row['Home Goals']}:{row['Away Goals']}"
            })
            rankings.append({
                'Team Tag': row['Away Tag'], 
                'Rank': row['Away Team Rank'], 
                'Matchday': md,
                'Opponent': row['Home Tag'],
                'Location': 'A',
                'Score': f"{row['Away Goals']}:{row['Home Goals']}"
            })

    df_rankings = pd.DataFrame(rankings)

    # Use plotly.graph_objs for better control over the animation
    fig = go.Figure()

    # Iterate through each team and add traces for the animation
    for team_tag in df_rankings['Team Tag'].unique():
        team_data = df_rankings[df_rankings['Team Tag'] == team_tag]
        primary_color, _ = get_team_colors(team_tag, color_codes_df)

        if primary_color.lower() == '#000000' or primary_color.lower() == 'black':
            primary_color = '#FFFFFF'  # Use white color for better visibility

        fig.add_trace(go.Scatter(
            x=team_data['Matchday'],
            y=team_data['Rank'],
            mode='lines+markers',
            marker=dict(size=8, color=primary_color),
            line=dict(width=3, color=primary_color),
            name=team_tag,
            text=[
                f"vs. {row['Opponent']} ({row['Location']})<br>{row['Score']}"
                for _, row in team_data.iterrows()
            ],
            hoverinfo='text',
        ))

    # Create animation frames
    frames = []
    for md in range(1, selected_matchday + 1):  # Include the selected matchday in the animation
        frame_data = []
        for team_tag in df_rankings['Team Tag'].unique():
            team_data = df_rankings[df_rankings['Team Tag'] == team_tag]
            primary_color, _ = get_team_colors(team_tag, color_codes_df)

            if primary_color.lower() == '#000000' or primary_color.lower() == 'black':
                primary_color = '#FFFFFF'  # Use white color for better visibility

            frame_data.append(go.Scatter(
                x=team_data['Matchday'][team_data['Matchday'] <= md],
                y=team_data['Rank'][team_data['Matchday'] <= md],
                mode='lines+markers',
                marker=dict(size=8, color=primary_color),
                line=dict(width=3, color=primary_color),
                name=team_tag,
            ))
        frames.append(go.Frame(data=frame_data, name=str(md)))

    fig.frames = frames

    # Update the layout for the animation
    fig.update_layout(
        title=f'Bundesliga Bump Chart Animation: League Position by Matchday ({selected_season})',
        xaxis=dict(
            title='Matchday',
            tickmode='linear',
            tick0=1,
            dtick=1,
            range=[0.5, 34.9],  # Extra space on the right
            showgrid=True,
            tickvals=list(range(1, 35)),
            ticktext=[str(i) for i in range(1, 35)],  # Ensure all matchdays 1-34 are shown
        ),
        yaxis=dict(
            title='Rank',
            autorange='reversed',
            tickvals=list(range(1, 19)),
            range=[0.5, 18.5],  # Adjusted range to reduce space
            showgrid=True
        ),
        plot_bgcolor='rgba(14, 17, 23, 0.70)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=800,
        width=1000,
        showlegend=False,
    )

    # Add a vertical grid line at the halfway mark (between 17th and 18th matchday)
    fig.add_vline(x=17.5, line=dict(color='rgba(255, 255, 255, 0.5)', dash='dot', width=1.5))

    # Add play/pause buttons and a progress bar for the animation, positioned next to each other
    fig.update_layout(
        updatemenus=[dict(type="buttons",
                          showactive=False,
                          direction="left",
                          x=0.1,  # Positioning
                          y=-0.2,  # Positioning just below the chart
                          buttons=[dict(label="Play",
                                        method="animate",
                                        args=[None, {"frame": {"duration": 500, "redraw": True},
                                                     "fromcurrent": True}]),
                                   dict(label="Pause",
                                        method="animate",
                                        args=[[None], {"frame": {"duration": 0, "redraw": False},
                                                       "mode": "immediate"}])])],
        sliders=[dict(
            steps=[dict(method="animate",
                        args=[[str(md)], {"mode": "immediate",
                                          "frame": {"duration": 500, "redraw": True},
                                          "transition": {"duration": 0}}],
                        label=str(md)) for md in range(1, selected_matchday + 1)],  # Include up to the selected matchday
            active=0,
            transition={"duration": 0},
            x=0.3,  # Align with the buttons
            y=-0.2,  # Same vertical position as the buttons
            xanchor="left",
            len=0.6,
        )]
    )

    st.plotly_chart(fig, use_container_width=True)

def display_bump_chart(df, selected_season, matchday, color_codes_df):
    st.header("Bump Chart")
    plot_bump_chart(df, color_codes_df, selected_season, matchday)
    
    st.subheader("Play Animation")
    if st.button("Play Animation", key="bump_chart_animation"):
        animate_bump_chart(df, color_codes_df, selected_season, matchday)

