pie_chart_prompt_template = """
You are looking at a pie chart that visualizes the distribution of your prediction outcomes for Bundesliga matches. This chart helps you understand how often you correctly predict wins, draws, and losses.

For {player_name}, the data shows:
- Win predictions: {win_percentage}% correct
- Draw predictions: {draw_percentage}% correct
- Loss predictions: {lose_percentage}% correct

Given that approximately {actual_draw_percentage}% of Bundesliga matches end in a draw, but you only predict draws {user_draw_percentage}% of the time, you may want to consider predicting more draws in the future. Improving your draw predictions could enhance your overall accuracy.
"""