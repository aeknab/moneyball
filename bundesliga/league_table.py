import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from bundesliga.crosstable import display_cross_table_view
from bundesliga.utils import get_team_colors, resize_image_to_bounding_box, image_to_base64
from bundesliga.home_away import filter_home_away_matches, calculate_home_away_points, plot_home_away_table
from bundesliga.first_and_second import filter_leg_matches, calculate_leg_points, plot_leg_table

# Function to filter matches based on the season and matchday
def filter_matches(df, selected_season, matchday):
    if selected_season == '2023/24':
        # Exclude data from the selected matchday for 2023/24 season (preview mode)
        return df[(df['Season'] == selected_season) & (df['Matchday'] < matchday)]
    else:
        # Include data from the selected matchday for 2005/06 to 2022/23 seasons
        return df[(df['Season'] == selected_season) & (df['Matchday'] <= matchday)]

# Function to calculate team points
def calculate_team_points(df_filtered):
    points_data = []

    for index, row in df_filtered.iterrows():
        points_data.append((row['Home Tag'], row['Home Team Points']))
        points_data.append((row['Away Tag'], row['Away Team Points']))

    df_points = pd.DataFrame(points_data, columns=['Team Tag', 'Points']).groupby('Team Tag').max().reset_index()

    return df_points.sort_values(by='Points', ascending=False)

# Function to plot the static league table with team logos
def plot_league_table(df_points, title, color_codes_df):
    fig = go.Figure()

    for i, (team_tag, points) in enumerate(zip(df_points['Team Tag'], df_points['Points'])):
        primary_color, secondary_color = get_team_colors(team_tag, color_codes_df)

        # Add the bar for the team with a white outline
        fig.add_trace(go.Bar(
            y=[i + 1],
            x=[points],
            orientation='h',
            marker=dict(
                color=primary_color,
                line=dict(color='white', width=0.5)  # Add white outlines with 2px width
            ),
            name=team_tag,
            showlegend=False  # Hide the legend for each bar
        ))

        # Load and resize team logo
        logo_path = f"data/logos/team_logos/{team_tag}.svg.png"
        team_logo = Image.open(logo_path)
        team_logo_resized = resize_image_to_bounding_box(team_logo, target_width=40, target_height=40)
        logo_base64 = image_to_base64(team_logo_resized)

        # Position the logo to the right of the bar
        fig.add_layout_image(
            dict(
                source=f'data:image/png;base64,{logo_base64}',
                xref="x", yref="y",
                x=points + 1,
                y=i + 1,
                sizex=7,
                sizey=0.6,
                xanchor="left",
                yanchor="middle",
                layer="above"
            )
        )

    fig.update_layout(
        title=title,
        xaxis=dict(title='Points', showgrid=False, zeroline=False, range=[0, 100]),
        yaxis=dict(showgrid=False, zeroline=False, tickvals=list(range(1, 19)), ticktext=list(range(1, 19)), autorange="reversed"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=80, b=40),
        height=800,
        width=1000
    )

    st.plotly_chart(fig, use_container_width=True)

# Function to get the points of each team at the end of each matchday for animation
def get_team_points_per_matchday(df_filtered):
    home_points = df_filtered[['Matchday', 'Home Tag', 'Home Team Points']].rename(
        columns={'Home Tag': 'Team Tag', 'Home Team Points': 'Points'}
    )
    away_points = df_filtered[['Matchday', 'Away Tag', 'Away Team Points']].rename(
        columns={'Away Tag': 'Team Tag', 'Away Team Points': 'Points'}
    )

    df_points = pd.concat([home_points, away_points]).drop_duplicates().sort_values(by=['Matchday', 'Points'], ascending=[True, False])
    df_points['Rank'] = df_points.groupby('Matchday')['Points'].rank(method='first', ascending=False)
    
    return df_points

# Function to create the animated league table with logos, highlighting only the selected teams
def create_league_table_animation(df_points, color_codes_df, selected_teams):
    # Merge with color data
    df_points = df_points.merge(color_codes_df[['Tag', 'Primary', 'Secondary']], how='left', left_on='Team Tag', right_on='Tag')

    # Ensure all matchdays up to 34 are included in the animation frames
    df_points['Matchday'] = df_points['Matchday'].astype(int)
    matchdays = list(range(1, 35))  # Explicitly define matchdays from 1 to 34

    # Create a complete DataFrame to ensure every team has data for every matchday
    all_teams = df_points['Team Tag'].unique()
    complete_index = pd.MultiIndex.from_product([matchdays, all_teams], names=['Matchday', 'Team Tag'])
    df_points = df_points.set_index(['Matchday', 'Team Tag']).reindex(complete_index, fill_value=0).reset_index()

    # Sort teams by rank for each matchday
    df_points['Rank'] = df_points.groupby('Matchday')['Points'].rank(method='first', ascending=False)

    # Initialize the figure
    fig = go.Figure()

    # Create initial bars and logos for the first matchday
    matchday = 1
    df_day = df_points[df_points['Matchday'] == matchday]
    
    for i, row in df_day.iterrows():
        team_tag = row['Team Tag']
        points = row['Points']
        rank = row['Rank']

        # Determine color based on whether the team is selected or not
        if team_tag in selected_teams:
            primary_color = row['Primary']
        else:
            primary_color = 'rgba(179, 179, 179, 0.75)'  # Greyed out with reduced opacity

        # Add bars
        fig.add_trace(go.Bar(
            x=[points],
            y=[rank],
            orientation='h',
            marker=dict(
                color=primary_color,
                line=dict(color='white', width=0.5)  # White outlines with reduced width
            ),
            name=team_tag,
            showlegend=False
        ))

    # Update layout
    fig.update_layout(
        yaxis=dict(autorange="reversed", title='Rank', tickvals=list(range(1, 19))),
        xaxis=dict(title='Points', range=[0, 100]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=800,
        width=1000
    )

    # Add the logos as layout images for the first frame
    layout_images = []
    for _, row in df_day.iterrows():
        team_tag = row['Team Tag']
        rank = row['Rank']
        points = row['Points']

        logo_path = f"data/logos/team_logos/{team_tag}.svg.png"
        team_logo = Image.open(logo_path)
        team_logo_resized = resize_image_to_bounding_box(team_logo, target_width=40, target_height=40)
        logo_base64 = image_to_base64(team_logo_resized)

        layout_images.append(
            dict(
                source=f'data:image/png;base64,{logo_base64}',
                xref="x",
                yref="y",
                x=points + 1,
                y=rank,
                sizex=5,
                sizey=0.7,
                xanchor="left",
                yanchor="middle",
                layer="above"
            )
        )

    # Update the layout with the images
    fig.update_layout(images=layout_images)

    # Generate frames for each matchday
    frames = []
    for matchday in matchdays:
        df_day = df_points[df_points['Matchday'] == matchday]
        frame_data = []
        layout_images_frame = []

        for i, row in df_day.iterrows():
            team_tag = row['Team Tag']
            points = row['Points']
            rank = row['Rank']

            # Determine color based on whether the team is selected or not
            if team_tag in selected_teams:
                primary_color = row['Primary']
            else:
                primary_color = 'rgba(179, 179, 179, 0.75)'  # Greyed out with reduced opacity

            # Update bars instead of replacing them
            frame_data.append(go.Bar(
                x=[points],
                y=[rank],
                orientation='h',
                marker=dict(
                    color=primary_color,
                    line=dict(color='white', width=0.5)
                ),
                name=team_tag,
                showlegend=False
            ))

            # Add logo image update for the frame
            logo_path = f"data/logos/team_logos/{team_tag}.svg.png"
            team_logo = Image.open(logo_path)
            team_logo_resized = resize_image_to_bounding_box(team_logo, target_width=40, target_height=40)
            logo_base64 = image_to_base64(team_logo_resized)

            layout_images_frame.append(
                dict(
                    source=f'data:image/png;base64,{logo_base64}',
                    xref="x",
                    yref="y",
                    x=points + 1,
                    y=rank,
                    sizex=5,
                    sizey=0.7,
                    xanchor="left",
                    yanchor="middle",
                    layer="above"
                )
            )

        frames.append(go.Frame(data=frame_data, layout=dict(images=layout_images_frame), name=str(matchday)))

    # Add frames to the figure
    fig.frames = frames

    # Move the buttons to the left and the slider to the right
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                x=0.05,  # Position on the left
                y=-0.1,  # Position below the chart
                showactive=True,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, {"frame": {"duration": 500, "redraw": True}, 
                                     "fromcurrent": True, 
                                     "mode": "immediate"}]
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0, "redraw": False}, 
                                       "mode": "immediate"}]
                    )
                ]
            )
        ],
        sliders=[{
            "steps": [{"args": [[str(i)], {"frame": {"duration": 500, "redraw": True}, 
                                           "mode": "immediate"}],
                       "label": str(i),
                       "method": "animate"} for i in matchdays],
            "currentvalue": {"prefix": "Matchday: "},
            "xanchor": "right",
            "x": 0.55,  # Position to the right of the buttons
            "len": 0.4,
            "pad": {"b": 10},
        }],
        newshape_line=dict(color="rgba(0,0,0,0)", width=0.5)  # No visible lines around frames
    )

    st.plotly_chart(fig, use_container_width=True)

# Function to display the league tables with animation and cross table
def display_league_tables(df, selected_season, matchday, view_selection, color_codes_df, selected_teams):

    # Ensure view selection is consistent across buttons
    df_filtered = filter_matches(df, selected_season, matchday)

    if view_selection == "Season Table":
        df_points = calculate_team_points(df_filtered)
        plot_league_table(df_points, f'Bundesliga League Table After Matchday {matchday} ({selected_season})', color_codes_df)

    elif view_selection == "Home/Away":
        # Display Home and Away tables one after the other
        st.subheader("Home Table")
        df_home_points = calculate_home_away_points(df_filtered, home_away='home')
        home_fig = plot_home_away_table(df_home_points, f'Home Table After Matchday {matchday} ({selected_season})', color_codes_df, home_away='home')
        st.plotly_chart(home_fig, use_container_width=True)

        st.subheader("Away Table")
        df_away_points = calculate_home_away_points(df_filtered, home_away='away')
        away_fig = plot_home_away_table(df_away_points, f'Away Table After Matchday {matchday} ({selected_season})', color_codes_df, home_away='away')
        st.plotly_chart(away_fig, use_container_width=True)

    elif view_selection == "1st/2nd Leg":
        # Display 1st and 2nd Leg tables one after the other
        st.subheader("1st Leg Table")
        df_leg_1 = filter_leg_matches(df, selected_season, leg='1st', matchday=matchday)
        if df_leg_1.empty:
            st.write("No available data yet.")
        else:
            df_leg_1_points = calculate_leg_points(df_leg_1)
            leg_1_fig = plot_leg_table(df_leg_1_points, f'1st Leg Table After Matchday {matchday} ({selected_season})', color_codes_df)
            st.plotly_chart(leg_1_fig, use_container_width=True)

        st.subheader("2nd Leg Table")
        df_leg_2 = filter_leg_matches(df, selected_season, leg='2nd', matchday=matchday)
        if df_leg_2.empty:
            st.write("No available data yet.")
        else:
            df_leg_2_points = calculate_leg_points(df_leg_2)
            leg_2_fig = plot_leg_table(df_leg_2_points, f'2nd Leg Table After Matchday {matchday} ({selected_season})', color_codes_df)
            st.plotly_chart(leg_2_fig, use_container_width=True)

    elif view_selection == "Cross Table":
        display_cross_table_view(df, selected_season, matchday)

    # Sub-header for animation
    if st.button("Play Animation"):
        df_points = get_team_points_per_matchday(df_filtered)
        create_league_table_animation(df_points, color_codes_df, selected_teams)