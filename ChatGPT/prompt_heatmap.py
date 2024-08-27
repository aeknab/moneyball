heat_map_prompt_template = """
The heat map visualizes areas where your predictions have been most and least accurate. Hotter areas indicate where you tend to predict accurately, while cooler areas show where you might struggle.

For {player_name}, the data reveals that your predictions are strongest in matches involving top-tier teams ({hot_zone_success_rate}% accuracy in 'hot zones'). However, you tend to struggle with predictions in lower-tier matches.

To improve, focus on analyzing matches involving lower-ranked teams more closely. A deeper dive into team form and head-to-head stats might help boost your accuracy in these cooler areas.
"""