import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import base64
from io import BytesIO

def generate_form_guide_plotly(team, team_tag, matchday, df_season, is_current_season):
    # Adjust matchday filtering based on the season
    if is_current_season:
        matchday_condition = df_season['Matchday'] < matchday  # Exclude current matchday for previews
    else:
        matchday_condition = df_season['Matchday'] <= matchday  # Include current matchday for past seasons

    # Check if there are previous matches
    if matchday <= 1:
        st.write(f"No previous match data available for {team}.")
        return None, None, None, None, None, None, None

    previous_matches = df_season[
        matchday_condition & 
        ((df_season['Home Team'] == team) | (df_season['Away Team'] == team))
    ]

    if previous_matches.empty:
        st.write(f"No previous match data available for {team}.")
        return None, None, None, None, None, None, None

    # Calculate Wins, Ties, and Losses
    wins = len(previous_matches[
        ((previous_matches['Home Team'] == team) & (previous_matches['Home Goals'] > previous_matches['Away Goals'])) |
        ((previous_matches['Away Team'] == team) & (previous_matches['Away Goals'] > previous_matches['Home Goals']))
    ])

    ties = len(previous_matches[
        previous_matches['Home Goals'] == previous_matches['Away Goals']
    ])

    losses = len(previous_matches[
        ((previous_matches['Home Team'] == team) & (previous_matches['Home Goals'] < previous_matches['Away Goals'])) |
        ((previous_matches['Away Team'] == team) & (previous_matches['Away Goals'] < previous_matches['Home Goals']))
    ])

    # Calculate the average goals and rankings
    total_games = wins + ties + losses
    avg_goals_scored = avg_goals_conceded = offensive_rank = defensive_rank = home_away_rank = clean_sheet_percentage = None

    if total_games > 0:
        avg_goals_scored = (
            previous_matches[previous_matches['Home Team'] == team]['Home Goals'].sum() +
            previous_matches[previous_matches['Away Team'] == team]['Away Goals'].sum()
        ) / total_games

        avg_goals_conceded = (
            previous_matches[previous_matches['Home Team'] == team]['Away Goals'].sum() +
            previous_matches[previous_matches['Away Team'] == team]['Home Goals'].sum()
        ) / total_games

        latest_match_row = previous_matches.iloc[-1]
        offensive_rank = latest_match_row['Home Team Offensive Ranking'] if latest_match_row['Home Team'] == team else latest_match_row['Away Team Offensive Ranking']
        defensive_rank = latest_match_row['Home Team Defensive Ranking'] if latest_match_row['Home Team'] == team else latest_match_row['Away Team Defensive Ranking']
        home_away_rank = latest_match_row['Home Team Home Ranking'] if latest_match_row['Home Team'] == team else latest_match_row['Away Team Away Ranking']
        clean_sheet_percentage = latest_match_row['Home Team Clean Sheet %'] if latest_match_row['Home Team'] == team else latest_match_row['Away Team Clean Sheet %']

    # Donut chart data
    labels = ['W', 'T', 'L']  # Labels for the chart itself
    values = [wins, ties, losses]
    colors = ['#a8e6a1', '#c4c4c4', '#ff9999']

    # Define the new border colors
    border_colors = ['#388e3c', '#999999', '#c62828']  # Green for wins, grey for ties, red for losses

    # Custom labels for the hover info
    hover_labels = ['Wins', 'Ties', 'Losses']

    # Create the donut chart using Plotly with borders
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.6,
        marker=dict(
            colors=colors,
            line=dict(color=border_colors, width=2)  # Add border colors and set width
        ),
        textinfo='text',
        text=[f"<b>{label}</b><br>{value}" for label, value in zip(labels, values)],
        hoverinfo='label+percent',
        customdata=hover_labels,  # Attach the custom hover labels
        hovertemplate='%{customdata}: %{percent:.1%}<extra></extra>'  # Customize hover format
    )])


    # Load the team logo and convert it to a base64 string
    logo_path = f"data/logos/team_logos/{team_tag}.svg.png"
    logo = Image.open(logo_path)
    buffer = BytesIO()
    logo.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    # Add the logo in the center of the donut (increase size)
    fig.add_layout_image(
        dict(
            source=f'data:image/png;base64,{img_str}',
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=0.3, sizey=0.3,  # Increase size for better fit
            xanchor="center", yanchor="middle"
        )
    )

    # Update layout for aesthetics
    fig.update_layout(
        showlegend=False,  # Hide the legend
        margin=dict(t=5, b=5, l=0, r=0),  # Adjust margins for a tighter fit
        annotations=[dict(text='', showarrow=False, font_size=20)],
        hovermode='closest',
        height=200,  # Set the height to make it smaller
        width=200,   # Set the width to make it smaller
    )

    return fig, avg_goals_scored, avg_goals_conceded, offensive_rank, defensive_rank, home_away_rank, clean_sheet_percentage

# Function to display two donut charts side by side with stats in the corners
def create_stat_box(fig, avg_goals_scored, avg_goals_conceded, offensive_rank, defensive_rank, home_away_rank, clean_sheet_percentage, is_home_team=True):
    # Display the donut chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Determine whether to label as Home Rank or Away Rank
    rank_label = "Home Rank" if is_home_team else "Away Rank"
    
    # Create a box below the chart with a grid for the statistics, now with the requested border
    st.markdown(
        f"""
        <div style="border: 2px solid #999999; border-radius: 15px; padding: 10px; width: 100%; height: auto; text-align: center; background-color: rgba(255, 255, 255, 0.35); box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);">
            <div style="display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr 1fr; gap: 10px;">
                <div style="font-size: 12px; padding: 5px; background-color: rgba(14, 17, 23, 0.7);"><b>Avg Goals Scored:</b><br>{avg_goals_scored:.2f}</div>
                <div style="font-size: 12px; padding: 5px; background-color: rgba(14, 17, 23, 0.7);"><b>Avg Goals Conceded:</b><br>{avg_goals_conceded:.2f}</div>
                <div style="font-size: 12px; padding: 5px; background-color: rgba(14, 17, 23, 0.7);"><b>Offensive Rank:</b><br>{offensive_rank}</div>
                <div style="font-size: 12px; padding: 5px; background-color: rgba(14, 17, 23, 0.7);"><b>Defensive Rank:</b><br>{defensive_rank}</div>
                <div style="font-size: 12px; padding: 5px; background-color: rgba(14, 17, 23, 0.7);"><b>{rank_label}:</b><br>{home_away_rank}</div>
                <div style="font-size: 12px; padding: 5px; background-color: rgba(14, 17, 23, 0.7);"><b>Clean Sheet %:</b><br>{clean_sheet_percentage:.1f}%</div>
            </div>
        </div>""", 
        unsafe_allow_html=True
    )

def display_donut_charts_side_by_side(home_team, away_team, home_team_tag, away_team_tag, matchday, df_season):
    col1, col2, col3 = st.columns([4, 1, 4])  # Adjust column proportions as needed

    # Determine if the selected season is the current one (2023/24)
    is_current_season = df_season['Season'].iloc[0] == '2023/24'

    with col1:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)  # Adjust the margin-top value as needed
        st.subheader(f"{home_team_tag} Season")
        fig_home, avg_goals_scored, avg_goals_conceded, offensive_rank, defensive_rank, home_away_rank, clean_sheet_percentage = generate_form_guide_plotly(home_team, home_team_tag, matchday, df_season, is_current_season)
        if fig_home:
            create_stat_box(fig_home, avg_goals_scored, avg_goals_conceded, offensive_rank, defensive_rank, home_away_rank, clean_sheet_percentage, is_home_team=True)

    with col3:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)  # Adjust the margin-top value as needed
        st.subheader(f"{away_team_tag} Season")
        fig_away, avg_goals_scored, avg_goals_conceded, offensive_rank, defensive_rank, home_away_rank, clean_sheet_percentage = generate_form_guide_plotly(away_team, away_team_tag, matchday, df_season, is_current_season)
        if fig_away:
            create_stat_box(fig_away, avg_goals_scored, avg_goals_conceded, offensive_rank, defensive_rank, home_away_rank, clean_sheet_percentage, is_home_team=False)