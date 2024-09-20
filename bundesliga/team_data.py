# team_data.py

def get_team_data(df_season, team_tag, matchday, is_current_season):
    if is_current_season:
        previous_matchday = matchday - 1
    else:
        previous_matchday = matchday

    earlier_matchday = previous_matchday - 1

    if previous_matchday <= 0:
        return {
            'rank': '--',
            'points': '--',
            'goals_scored': '--',
            'goals_conceded': '--',
            'gd': '--',
            'previous_rank': '--',
            'games': 0,
            'wins': 0,
            'ties': 0,
            'losses': 0,
            'movement': '--'  # Add default movement
        }

    # Filter up to the appropriate matchday
    df_filtered = df_season[df_season['Matchday'] <= previous_matchday]
    df_earlier = df_season[df_season['Matchday'] <= earlier_matchday]

    # Calculate the stats up to the appropriate matchday
    games = len(df_filtered[(df_filtered['Home Tag'] == team_tag) | (df_filtered['Away Tag'] == team_tag)])
    wins = len(df_filtered[((df_filtered['Home Tag'] == team_tag) & (df_filtered['Home Goals'] > df_filtered['Away Goals'])) |
                            ((df_filtered['Away Tag'] == team_tag) & (df_filtered['Away Goals'] > df_filtered['Home Goals']))])
    ties = len(df_filtered[((df_filtered['Home Tag'] == team_tag) | (df_filtered['Away Tag'] == team_tag)) & 
                            (df_filtered['Home Goals'] == df_filtered['Away Goals'])])
    losses = games - (wins + ties)

    # Get current rank and points from the appropriate matchday
    current_match_row_home = df_filtered[(df_filtered['Matchday'] == previous_matchday) & (df_filtered['Home Tag'] == team_tag)]
    current_match_row_away = df_filtered[(df_filtered['Matchday'] == previous_matchday) & (df_filtered['Away Tag'] == team_tag)]

    if not current_match_row_home.empty:
        row = current_match_row_home.iloc[0]
        rank = row['Home Team Rank']
        points = row['Home Team Points']
        goals_scored = row['Home Team Goals Scored']
        goals_conceded = row['Home Team Goals Conceded']
        gd = row['Home Team GD']
    else:
        row = current_match_row_away.iloc[0]
        rank = row['Away Team Rank']
        points = row['Away Team Points']
        goals_scored = row['Away Team Goals Scored']
        goals_conceded = row['Away Team Goals Conceded']
        gd = row['Away Team GD']

    # Get previous rank for movement calculation
    earlier_match_row_home = df_earlier[(df_earlier['Matchday'] == earlier_matchday) & (df_earlier['Home Tag'] == team_tag)]
    earlier_match_row_away = df_earlier[(df_earlier['Matchday'] == earlier_matchday) & (df_earlier['Away Tag'] == team_tag)]

    if not earlier_match_row_home.empty:
        previous_rank = earlier_match_row_home.iloc[0]['Home Team Rank']
    elif not earlier_match_row_away.empty:
        previous_rank = earlier_match_row_away.iloc[0]['Away Team Rank']
    else:
        previous_rank = '--'

    # Calculate movement (if there is a previous rank)
    movement = get_movement(rank, previous_rank)

    return {
        'rank': rank,
        'points': points,
        'goals_scored': goals_scored,
        'goals_conceded': goals_conceded,
        'gd': gd,
        'previous_rank': previous_rank,
        'games': games,
        'wins': wins,
        'ties': ties,
        'losses': losses,
        'team_tag': team_tag,
        'movement': movement  # Ensure movement is returned
    }

def get_movement(rank, previous_rank):
    if previous_rank == '--' or rank == '--':
        return '--'
    elif int(rank) < int(previous_rank):
        return '⬆️'  # Moved up
    elif int(rank) > int(previous_rank):
        return '⬇️'  # Moved down
    else:
        return '⏺️'  # Stayed the same