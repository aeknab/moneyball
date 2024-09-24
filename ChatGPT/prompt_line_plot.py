line_plot_prompt_template = """
You are looking at a line plot that compares your predicted goals against the actual goals for each matchday. The plot also shows the prediction range for the group, helping you visualize how close or far your predictions are from both the group's average and the actual results.

For {player_name}, the trend over time indicates that your predictions are {trend_over_time}, suggesting that your performance is {trend_description}.

### Key Insights:
- **Average Predicted Goals**: On average, {player_avg_predicted_goals_line}
- **Average Actual Goals**: The actual number of goals scored in these matches is {avg_actual_goals}.
- **Accuracy**: You were within a 1-goal margin of the actual score in {within_range_percentage}% of matches.

### Areas for Improvement:
- **Overestimation**: You overestimated the number of goals in {overestimation_percentage}% of the matches. Try to account for lower-scoring games.
- **Underestimation**: You underestimated the number of goals in {underestimation_percentage}% of the matches. Consider revising your strategy for high-scoring games.
- **Prediction Range**: Your predictions fell within the group's prediction range {within_range_percentage}% of the time.

Focus on improving your consistency and narrowing your prediction range in future matchdays. Analyzing outliers and adjusting for specific teams could help improve your overall accuracy.
"""