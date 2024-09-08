def get_team_data(team_tag, matchday, is_current_season, predictions_mode=False, match_row=None, df_season=None):
    # Example logic for team data
    if predictions_mode:
        # Fetch data in predictions mode
        if team_tag == match_row['Home Tag']:
            return {
                'rank': match_row['Home Team Rank'],
                'points': match_row['Home Team Points'],
                # Add other fields here
            }
        else:
            return {
                'rank': match_row['Away Team Rank'],
                'points': match_row['Away Team Points'],
                # Add other fields here
            }

def get_movement(rank, previous_rank):
    if previous_rank == '--' or rank == '--':
        return '--'
    elif int(rank) < int(previous_rank):
        return '⬆️'
    elif int(rank) > int(previous_rank):
        return '⬇️'
    else:
        return '⏺️'