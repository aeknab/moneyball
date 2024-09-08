# match_preview_functions.py

import pandas as pd

def get_last_5_matches(df_season, team, matchday):
    previous_matches = df_season[((df_season['Home Team'] == team) | (df_season['Away Team'] == team)) & 
                                 (df_season['Matchday'] < matchday)].sort_values(by='Matchday', ascending=False).head(5)
    
    match_tags = []
    results = []
    outcomes = []
    
    for index, match in previous_matches.iterrows():
        if match['Home Team'] == team:
            opponent = match['Away Tag']
            score = f"{match['Home Goals']}:{match['Away Goals']}"
            if match['Home Goals'] > match['Away Goals']:
                result = 'W'
            elif match['Home Goals'] < match['Away Goals']:
                result = 'L'
            else:
                result = 'T'
        else:
            opponent = match['Home Tag']
            score = f"{match['Away Goals']}:{match['Home Goals']}"
            if match['Away Goals'] > match['Home Goals']:
                result = 'W'
            elif match['Away Goals'] < match['Home Goals']:
                result = 'L'
            else:
                result = 'T'
        
        match_tags.append(opponent)
        results.append(result)
        outcomes.append(score)
    
    total_matches = len(previous_matches)
    return match_tags, results, outcomes, total_matches

def get_last_10_meetings(df, home_team_tag, away_team_tag, color_codes_df, current_matchday, current_season):
    matches_between_teams = df[
        ((df['Home Tag'] == home_team_tag) & (df['Away Tag'] == away_team_tag)) | 
        ((df['Home Tag'] == away_team_tag) & (df['Away Tag'] == home_team_tag))
    ]
    
    matches_between_teams = matches_between_teams[
        ~((matches_between_teams['Season'] == current_season) & (matches_between_teams['Matchday'] >= current_matchday))
    ].sort_values(by='Match Date', ascending=False).head(10)
    
    team1_wins = 0
    team2_wins = 0
    draws = 0

    total_matches = len(matches_between_teams)

    for _, match in matches_between_teams.iterrows():
        if match['Home Tag'] == home_team_tag:
            if match['Home Goals'] > match['Away Goals']:
                team1_wins += 1
            elif match['Home Goals'] < match['Away Goals']:
                team2_wins += 1
            else:
                draws += 1
        elif match['Home Tag'] == away_team_tag:
            if match['Home Goals'] > match['Away Goals']:
                team2_wins += 1
            elif match['Home Goals'] < match['Away Goals']:
                team1_wins += 1
            else:
                draws += 1

    home_primary, home_secondary = get_team_colors(home_team_tag, color_codes_df)
    away_primary, away_secondary = get_team_colors(away_team_tag, color_codes_df)
    
    away_color = away_primary
    
    return team1_wins, team2_wins, draws, home_primary, away_color, total_matches

def plot_last_10_meetings(df, home_team_tag, away_team_tag, color_codes_df, current_matchday, current_season):
    team1_wins, team2_wins, draws, home_color, away_color, total_matches = get_last_10_meetings(
        df, home_team_tag, away_team_tag, color_codes_df, current_matchday, current_season
    )
    
    st.subheader(f"Last {total_matches} Meeting{'s' if total_matches > 1 else ''}")
    
    if total_matches > 0:
        proportions = [team1_wins / total_matches, draws / total_matches, team2_wins / total_matches]
        
        home_primary, home_secondary = get_team_colors(home_team_tag, color_codes_df)
        away_primary, away_secondary = get_team_colors(away_team_tag, color_codes_df)
        
        fig, ax = plt.subplots(figsize=(8, 2))
        
        ax.barh(0, proportions[0], color=home_primary, hatch='///', edgecolor=home_secondary, height=1)
        ax.barh(0, proportions[1], left=proportions[0], color='#BBBBBB', hatch='///', edgecolor='#FFFFFF', height=1)
        ax.barh(0, proportions[2], left=proportions[0] + proportions[1], color=away_primary, hatch='///', edgecolor=away_secondary, height=1)

        ax.axis('off')
        
        home_logo_path = f"data/logos/{home_team_tag}.svg.png"
        away_logo_path = f"data/logos/{away_team_tag}.svg.png"
        
        home_logo = load_image(home_logo_path)
        away_logo = load_image(away_logo_path)
        
        home_logo = home_logo.convert("RGBA")
        away_logo = away_logo.convert("RGBA")
        
        max_width = 30
        max_height = 30
        
        home_logo_resized = resize_image(home_logo, max_width, max_height)
        away_logo_resized = resize_image(away_logo, max_width, max_height)
        
        home_logo_array = np.array(home_logo_resized)
        away_logo_array = np.array(away_logo_resized)
        
        ab_home = AnnotationBbox(OffsetImage(home_logo_array, zoom=0.6), (0.02, -0.55), frameon=False, box_alignment=(0.5, 0.5))
        ab_away = AnnotationBbox(OffsetImage(away_logo_array, zoom=0.6), (0.98, -0.55), frameon=False, box_alignment=(0.5, 0.5))
        
        ax.add_artist(ab_home)
        ax.add_artist(ab_away)
        
        ax.text(0.05, -0.55, f'{team1_wins} Wins', ha='left', va='center', fontsize=10)
        ax.text(0.5, -0.55, f'{draws} Ties', ha='center', va='center', fontsize=10)
        ax.text(0.95, -0.55, f'{team2_wins} Wins', ha='right', va='center', fontsize=10)

        plt.subplots_adjust(bottom=0.6)

        st.pyplot(fig)
    else:
        st.write(f"No previous matches between {home_team_tag} and {away_team_tag}.")

def generate_form_guide(team, matchday, df_season):
    if matchday <= 1:
        st.write(f"No previous match data available for {team}.")
        return

    previous_matches = df_season[(df_season['Matchday'] < matchday) & 
                                 ((df_season['Home Team'] == team) | (df_season['Away Team'] == team))]

    if previous_matches.empty:
        st.write(f"No previous match data available for {team}.")
        return

    wins = len(previous_matches[((previous_matches['Home Team'] == team) & (previous_matches['Home Goals'] > previous_matches['Away Goals'])) |
                                ((previous_matches['Away Team'] == team) & (previous_matches['Away Goals'] > previous_matches['Home Goals']))])

    ties = len(previous_matches[previous_matches['Home Goals'] == previous_matches['Away Goals']])

    losses = len(previous_matches[((previous_matches['Home Team'] == team) & (previous_matches['Home Goals'] < previous_matches['Away Goals'])) |
                                  ((previous_matches['Away Team'] == team) & (previous_matches['Away Goals'] < previous_matches['Home Goals']))])

    total_games = wins + ties + losses
    if total_games > 0:
        win_pct = wins / total_games * 100
        tie_pct = ties / total_games * 100
        loss_pct = losses / total_games * 100
    else:
        win_pct = tie_pct = loss_pct = 0

    labels = ['Wins', 'Ties', 'Losses']
    sizes = [wins, ties, losses]
    colors = ['#a8e6a1', '#c4c4c4', '#ff9999']

    fig, ax = plt.subplots()
    wedges, texts = ax.pie(sizes, labels=None, colors=colors, startangle=140, pctdistance=0.85)

    center_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig.gca().add_artist(center_circle)
    ax.axis('equal')

    legend_labels = [f'{label} ({size}) - {pct:.1f}%' for label, size, pct in zip(labels, sizes, [win_pct, tie_pct, loss_pct])]
    ax.legend(wedges, legend_labels, loc='center', bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=False)

    st.pyplot(fig)

    if total_games > 0:
        avg_goals_scored = previous_matches[previous_matches['Home Team'] == team]['Home Goals'].mean() + previous_matches[previous_matches['Away Team'] == team]['Away Goals'].mean()
        avg_goals_conceded = previous_matches[previous_matches['Home Team'] == team]['Away Goals'].mean() + previous_matches[previous_matches['Away Team'] == team]['Home Goals'].mean()

        latest_match_row = previous_matches.iloc[-1]
        offensive_rank = latest_match_row['Home Team Offensive Ranking'] if latest_match_row['Home Team'] == team else latest_match_row['Away Team Offensive Ranking']
        defensive_rank = latest_match_row['Home Team Defensive Ranking'] if latest_match_row['Home Team'] == team else latest_match_row['Away Team Defensive Ranking']

        st.write(f"**Average Goals Scored:** {avg_goals_scored:.2f}")
        st.write(f"**Average Goals Conceded:** {avg_goals_conceded:.2f}")
        st.write(f"**Offensive Ranking:** {offensive_rank}")
        st.write(f"**Defensive Ranking:** {defensive_rank}")
    else:
        st.write("No data available for this matchday.")
