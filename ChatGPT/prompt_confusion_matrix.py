confusion_matrix_prompt_template = """
This confusion matrix displays your prediction accuracy by comparing predicted outcomes to actual results. It helps identify where your predictions align or differ from reality.

For {player_name}, the matrix shows:
- Accuracy: {accuracy}%
- Precision for wins: {precision}%
- Recall for losses: {recall}%

Your prediction accuracy could improve by focusing on better distinguishing between closely matched teams, especially in cases where you've had difficulty predicting losses. Consider revisiting your approach to games involving mid-table teams.
"""