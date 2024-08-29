import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from PIL import Image
from bundesliga.utils import get_team_colors, load_image, image_to_base64

def resize_image_uniform(image, target_size):
    original_width, original_height = image.size
    scaling_factor = target_size / min(original_width, original_height)
    new_width = int(original_width * scaling_factor)
    new_height = int(original_height * scaling_factor)
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    return resized_image

def filter_matches_for_season(df, selected_season, matchday):
    if selected_season == '2023/24':
        return df[(df['Season'] == selected_season) & (df['Matchday'] < matchday)]
    else:
        return df[(df['Season'] == selected_season) & (df['Matchday'] <= matchday)]

def plot_bump_chart(df, color_codes_df, selected_season, matchday, selected_teams):
    df_season_before_matchday = filter_matches_for_season(df, selected_season, matchday)

    if not df_season_before_matchday.empty:
        rankings = []

        for md in range(1, matchday + 1):
            df_md = df_season_before_matchday[df_season_before_matchday['Matchday'] == md]
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
        df_bump = df_rankings.pivot(index='Team Tag', columns='Matchday', values='Rank')

        fig = go.Figure()

        for team_tag in df_bump.index:
            primary_color, _ = get_team_colors(team_tag, color_codes_df)
            if primary_color.lower() == '#000000' or primary_color.lower() == 'black':
                primary_color = '#FFFFFF'

            if team_tag not in selected_teams:
                primary_color = 'rgba(169,169,169,0.75)'  # Grey and 75% opacity for unselected teams

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
                text=hover_texts,
                hoverinfo='text'
            ))

            team_logo_path = f"data/logos/team_logos/{team_tag}.svg.png"
            team_logo = load_image(team_logo_path)
            target_size = 35
            team_logo_resized = resize_image_uniform(team_logo, target_size)
            logo_base64 = image_to_base64(team_logo_resized)

            end_x = df_bump.columns[-1]
            end_y = df_bump.loc[team_tag].iloc[-1]
            fig.add_layout_image(
                dict(
                    source=f'data:image/png;base64,{logo_base64}',
                    xref="x", yref="y",
                    x=end_x + 0.4,
                    y=end_y,
                    sizex=1,
                    sizey=1,
                    xanchor="left",
                    yanchor="middle"
                )
            )

        fig.update_layout(
            title=f'Bundesliga Bump Chart: League Position by Matchday ({selected_season})',
            xaxis=dict(
                title='Matchday', 
                tickmode='array', 
                tickvals=list(range(1, 35)),
                ticktext=[str(i) for i in range(1, 35)],
                dtick=1,
                range=[0.5, 35.5],
                showgrid=True,
            ),
            yaxis=dict(
                title='Rank', 
                autorange='reversed', 
                tickvals=list(range(1, 19)), 
                range=[0.5, 18.5],
                showgrid=True
            ),
            plot_bgcolor='rgba(14, 17, 23, 0.70)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=800,
            width=1000,
            showlegend=False,
        )

        fig.add_vline(x=17.5, line=dict(color='rgba(255, 255, 255, 0.5)', dash='dot', width=1.5))
    
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No data available for bump chart.")

def animate_bump_chart(df, color_codes_df, selected_season, selected_matchday, selected_teams):
    df_season = filter_matches_for_season(df, selected_season, selected_matchday)
    rankings = []

    for md in range(1, selected_matchday + 1):
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

    fig = go.Figure()

    for team_tag in df_rankings['Team Tag'].unique():
        team_data = df_rankings[df_rankings['Team Tag'] == team_tag]
        primary_color, _ = get_team_colors(team_tag, color_codes_df)

        if primary_color.lower() == '#000000' or primary_color.lower() == 'black':
            primary_color = '#FFFFFF'

        if team_tag not in selected_teams:
            primary_color = 'rgba(169,169,169,0.75)'  # Grey and 75% opacity for unselected teams

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

    frames = []
    for md in range(1, selected_matchday + 1):
        frame_data = []
        layout_images_frame = []

        for team_tag in df_rankings['Team Tag'].unique():
            team_data = df_rankings[df_rankings['Team Tag'] == team_tag]
            primary_color, _ = get_team_colors(team_tag, color_codes_df)

            if primary_color.lower() == '#000000' or primary_color.lower() == 'black':
                primary_color = '#FFFFFF'

            if team_tag not in selected_teams:
                primary_color = 'rgba(169,169,169,0.75)'

            frame_data.append(go.Scatter(
                x=team_data['Matchday'][team_data['Matchday'] <= md],
                y=team_data['Rank'][team_data['Matchday'] <= md],
                mode='lines+markers',
                marker=dict(size=8, color=primary_color, symbol='circle'),
                line=dict(width=3, color=primary_color),
                name=team_tag,
            ))

            if not team_data['Rank'][team_data['Matchday'] == md].empty:
                end_x = md
                end_y = team_data['Rank'][team_data['Matchday'] == md].values[0]

                logo_path = f"data/logos/team_logos/{team_tag}.svg.png"
                team_logo = load_image(logo_path)
                target_size = 35
                team_logo_resized = resize_image_uniform(team_logo, target_size)
                logo_base64 = image_to_base64(team_logo_resized)

                layout_images_frame.append(
                    dict(
                        source=f'data:image/png;base64,{logo_base64}',
                        xref="x",
                        yref="y",
                        x=end_x + 0.4,
                        y=end_y,
                        sizex=1,
                        sizey=1,
                        xanchor="left",
                        yanchor="middle",
                        layer="above"
                    )
                )

        frames.append(go.Frame(data=frame_data, layout=dict(images=layout_images_frame), name=str(md)))

    fig.frames = frames

    fig.update_layout(
        updatemenus=[
            dict(type="buttons",
                showactive=False,
                direction="left",
                x=0.1,
                y=-0.2,
                buttons=[dict(label="Play",
                            method="animate",
                            args=[None, {"frame": {"duration": 500, "redraw": True},
                                            "fromcurrent": True, "transition": {"duration": 500}}]),
                        dict(label="Pause",
                            method="animate",
                            args=[[None], {"frame": {"duration": 0, "redraw": False},
                                            "mode": "immediate"}])])
        ],
        sliders=[dict(
            steps=[dict(method="animate",
                        args=[[str(md)], {"mode": "immediate",
                                        "frame": {"duration": 500, "redraw": True},
                                        "transition": {"duration": 500}}],
                        label=f"{md}") for md in range(1, 35)],
            active=0,
            transition={"duration": 0},
            x=0.3,
            y=-0.2,
            xanchor="left",
            len=0.6,
            currentvalue={"prefix": "Matchday ", "suffix": ""}
        )]
    )

    fig.update_layout(
        title=f'Bundesliga Bump Chart Animation: League Position by Matchday ({selected_season})',
        xaxis=dict(
            title='Matchday', 
            tickmode='array', 
            tickvals=list(range(1, 35)),
            ticktext=[str(i) for i in range(1, 35)],
            dtick=1,
            range=[0.5, 35.5],
            showgrid=True,
        ),
        yaxis=dict(
            title='Rank', 
            autorange='reversed', 
            tickvals=list(range(1, 19)), 
            range=[0.5, 18.5],
            showgrid=True
        ),
        plot_bgcolor='rgba(14, 17, 23, 0.70)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=800,
        width=1000,
        showlegend=False,
    )

    fig.add_vline(x=17.5, line=dict(color='rgba(255, 255, 255, 0.5)', dash='dot', width=1.5))

    st.plotly_chart(fig, use_container_width=True)

def display_bump_chart(df, selected_season, matchday, color_codes_df, selected_teams):
    st.header("Bump Chart")
    plot_bump_chart(df, color_codes_df, selected_season, matchday, selected_teams)
    
    if st.button("Play Animation", key="bump_chart_animation"):
        animate_bump_chart(df, color_codes_df, selected_season, matchday, selected_teams)