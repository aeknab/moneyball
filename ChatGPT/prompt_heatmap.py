heat_map_prompt_template = """
# Instructions for ChatGPT:
# You're interpreting a heat map for a player of a football predictions game, a la Kicktipp, who wants to compare his predictions against the actual predictions in a heat map.
# (1) Focus on the areas of greatest discrepancy between the player's predictions and actual results.
# (2) Cite specific numbers when comparing predictions to actual results.
# (3) Provide exactly three pieces of advice based on the analysis.
# (4) Here are the variables you can use in your analysis:

# Variables for analysis:
# - player_name: The name of the player being analyzed.
# - match_count: Total number of matches analyzed.
# - low_scoring_pred_count: Number of low-scoring games (0:0, 1:0, 0:1, 1:1) the player predicted.
# - low_scoring_actual_count: Number of low-scoring games that actually occurred.
# - under_over_predict_low: Whether the player under- or over-predicted low-scoring games.
# - high_scoring_pred_count: Number of high-scoring games (3+ goals for any team) the player predicted.
# - high_scoring_actual_count: Number of high-scoring games that actually occurred.
# - under_over_predict_high: Whether the player under- or over-predicted high-scoring games.
# - lopsided_pred_count: Number of lopsided games (goal difference of 3+ goals) predicted.
# - lopsided_actual_count: Number of lopsided games that actually occurred.
# - predicted_home_goals: Average number of home team goals predicted by the player.
# - actual_home_goals: Average number of home team goals that actually occurred.
# - home_away_goal_bias: Whether the player over- or underestimated home goals.
# - predicted_away_goals: Average number of away team goals predicted by the player.
# - actual_away_goals: Average number of away team goals that actually occurred.
# - home_away_goal_bias_away: Whether the player over- or underestimated away goals.
# - hot_zone_success_rate: Player's success rate in predicting goals in the hot zone (1-2 goals).
# - cold_zone_accuracy: Player's accuracy in predicting higher-scoring matches (3+ goals).

# ChatGPT should generate the analysis following the above instructions and use these variables.
"""