# groups/utils.py

def format_points(points):
    """Formats points with color based on the score."""
    if points == 0:
        return f"<span style='color:grey'>({points})</span>"
    elif points == 2:
        return f"<span style='color:yellow'>({points})</span>"
    elif points == 3:
        return f"<span style='color:orange'>({points})</span>"
    elif points == 4:
        return f"<span style='color:red'>({points})</span>"
    return f"({points})"

def calculate_points(pred_home, pred_away, actual_home, actual_away):
    """Calculates points based on prediction and actual results."""
    pred_diff = pred_home - pred_away
    actual_diff = actual_home - actual_away

    if pred_home == actual_home and pred_away == actual_away:
        return 4  # Exact score
    elif pred_diff == actual_diff:
        if pred_diff == 0:  # Both predicted and actual results are ties but with different scores
            return 2
        return 3  # Correct goal difference
    elif (pred_home > pred_away and actual_home > actual_away) or (pred_home < pred_away and actual_home < actual_away):
        return 2  # Correct outcome/tendency
    else:
        return 0  # Wrong prediction
