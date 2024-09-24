import streamlit as st
import pandas as pd
from analysis.pie_chart_group import display_group_pie_chart, calculate_pie_chart_data
from analysis.heat_map_group import display_group_heat_map, calculate_heat_map_data
from analysis.confusion_matrix import display_confusion_matrix, calculate_confusion_matrix_data
from analysis.line_plot import display_line_plot, calculate_line_plot_data
from ChatGPT.prompt_pie_chart import pie_chart_prompt_template
from ChatGPT.prompt_confusion_matrix import confusion_matrix_prompt_template
from ChatGPT.prompt_heatmap import heat_map_prompt_template
from ChatGPT.prompt_line_plot import line_plot_prompt_template
from openai import OpenAI

client = OpenAI(api_key="sk-o0hrLU1sy_khDaVw-sFP1pnIOP-SLylV1lC-gaOgLWT3BlbkFJ7b2I0vPST6fT6vgTB90vaf-DIDxpOg00Z8ax3cOhIA")

def calculate_prediction_accuracy(predicted_goals, actual_goals):
    """Calculate the accuracy of predictions."""
    correct_predictions = (predicted_goals == actual_goals).sum()
    total_predictions = len(predicted_goals)
    return correct_predictions / total_predictions * 100

def generate_pie_chart_analysis(selected_players, matchdays_df):
    # Unpack the tuple returned by calculate_pie_chart_data
    predictions, actual_results = calculate_pie_chart_data(matchdays_df, selected_players)

    try:
        # Calculate percentages using the correct dictionaries
        win_percentage = predictions['Home Win'] / sum(predictions.values()) * 100
        draw_percentage = predictions['Tie'] / sum(predictions.values()) * 100
        lose_percentage = predictions['Away Win'] / sum(predictions.values()) * 100

        user_draw_percentage = draw_percentage
        actual_draw_percentage = actual_results['Tie'] / sum(actual_results.values()) * 100

    except (KeyError, TypeError, ValueError) as e:
        st.error(f"An error occurred while accessing data: {e}")
        return None

    # Example data to fill placeholders
    example_player_name = selected_players[0] if selected_players else "Player"
    example_win_success_rate = 75  # Replace with actual calculation if available
    example_lose_success_rate = 60  # Replace with actual calculation if available

    # Ensure all placeholders in the template have corresponding values
    prompt = pie_chart_prompt_template.format(
        player_name=example_player_name,
        win_percentage=win_percentage,
        draw_percentage=draw_percentage,
        lose_percentage=lose_percentage,
        user_draw_percentage=user_draw_percentage,
        actual_draw_percentage=actual_draw_percentage,
        win_success_rate=example_win_success_rate,
        lose_success_rate=example_lose_success_rate
    )

    return generate_analysis(prompt)

def generate_confusion_matrix_analysis(selected_players, matchdays_df, matchday):
    # Calculate confusion matrix data
    data = calculate_confusion_matrix_data(matchdays_df, selected_players, matchday)

    # Calculate accuracy using the correct method
    accuracy = (data['confusion_matrix'].to_numpy().trace() / data['confusion_matrix'].values.sum()) * 100

    # Calculate precision and recall
    precision = data['confusion_matrix'].iloc[0, 0] / data['confusion_matrix'].iloc[0].sum() * 100
    recall = data['confusion_matrix'].iloc[0, 0] / data['confusion_matrix'].sum(axis=1).iloc[0] * 100

    # Use the first selected player as the player_name, or 'All Players' if multiple are selected
    player_name = selected_players[0] if len(selected_players) == 1 else "All Players"

    # Ensure all placeholders in the template have corresponding values
    prompt = confusion_matrix_prompt_template.format(
        player_name=player_name,
        accuracy=accuracy,
        precision=precision,
        recall=recall
    )

    return generate_analysis(prompt)

def generate_heat_map_analysis(selected_players, matchdays_df):
    # Calculate heat map data
    data = calculate_heat_map_data(matchdays_df, selected_players)

    # Access the tuple elements by index
    hot_zone_success_rate = data[0] * 100  # Assuming the hot zone success rate is the first element
    most_frequent_score = data[1]  # Assuming the most frequent score is the second element, which is a tuple

    # Convert the most frequent score tuple to a string (e.g., "3-1")
    most_frequent_score_str = f"{most_frequent_score[0]}-{most_frequent_score[1]}"

    # Use the first selected player as the player_name, or 'All Players' if multiple are selected
    player_name = selected_players[0] if len(selected_players) == 1 else "All Players"

    # Format the prompt with the retrieved data
    prompt = heat_map_prompt_template.format(
        player_name=player_name,
        hot_zone_success_rate=hot_zone_success_rate,
        most_frequent_score=most_frequent_score_str
    )

    return generate_analysis(prompt)

def generate_line_plot_analysis(selected_players, matchdays_df, matchday):
    # Calculate the line plot data and get the trend
    data = calculate_line_plot_data(matchdays_df, selected_players, matchday)

    # Access the trend data from the returned dictionary
    trend_over_time = data["trend_over_time"]
    trend_description = data["trend_description"]

    # Get the average predicted goals for the player, if available
    player_avg_predicted_goals = data.get("player_avg_predicted_goals", None)

    # Use the first selected player as the player_name, or 'All Players' if multiple are selected
    player_name = selected_players[0] if len(selected_players) == 1 else "All Players"

    # Tailor the analysis based on whether an individual player is selected
    if player_avg_predicted_goals is not None:
        player_avg_predicted_goals_line = f"you predicted an average of {player_avg_predicted_goals:.1f} goals per match, compared to the group's average of {data['avg_predicted_goals']:.1f}."
    else:
        player_avg_predicted_goals_line = f"the group's average predicted goals was {data['avg_predicted_goals']:.1f}."

    # Count exact hits, within target range, overestimation and underestimation based on the new criteria
    exact_hit_count = ((data["player_lines"][0]["y"] - data["actual_goals"]).abs() == 0).sum()
    within_range_count = ((data["player_lines"][0]["y"] - data["actual_goals"]).abs() <= 2).sum()
    overestimation_count = (data["player_lines"][0]["y"] > data["actual_goals"] + 2).sum()
    underestimation_count = (data["player_lines"][0]["y"] < data["actual_goals"] - 2).sum()

    total_predictions = len(data["actual_goals"])

    # Calculate percentages
    within_range_percentage = (within_range_count / total_predictions) * 100
    overestimation_percentage = (overestimation_count / total_predictions) * 100
    underestimation_percentage = (underestimation_count / total_predictions) * 100
    exact_hit_percentage = (exact_hit_count / total_predictions) * 100

    # Explanation of what a line plot is and its purpose, with revised description of prediction range
    line_plot_intro = f"""
    You're looking at the season in all its gritty detail. The line plot maps your predictions against the reality of goals scored.

    - **Predicted Goals Line**: That's you calling the shots, for better or worse.
    - **Actual Goals Line**: Cold, hard reality. That's what really happened on the pitch.
    - **Prediction Range**: The shaded area shows where your group mates stood with their guesses. It captures the highest and lowest predictions from the others in the group, excluding you. So now you know if you're too bold—or playing it too safe.
    """

    # Construct the personalized analysis with clear explanation of elements
    prompt = f"""
    Hey {player_name}, let's break it down.

    {line_plot_intro}

    So here's the deal: your predictions have been {trend_description} as the season wears on. Not exactly a winning streak, but not a total flop either.

    On average, {player_avg_predicted_goals_line} The actual goals scored in these matches? {data['avg_actual_goals']:.1f}. 

    You hit the nail on the head in {exact_hit_percentage:.1f}% of the matches. Close, but no cigar? You were within 2 goals of the mark in {within_range_percentage:.1f}% of the games. But hey, let's not sugarcoat it—you overshot by 3 or more goals in {overestimation_percentage:.1f}% of them and undershot by that much in {underestimation_percentage:.1f}% of the others.

    Now, here's the kicker: tighten up those predictions. It's all about reducing those big misses, and getting more of those exact hits. Balance, kid—that's the key. Learn from your misses, study the trends, and maybe, just maybe, you’ll come out on top next time.
    """

    return generate_analysis(prompt)

def generate_analysis(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"An error occurred while generating the analysis: {e}")
        return None

def display_analysis_section(matchday, rankings_df, matchdays_df, selected_player):
    players = sorted(rankings_df['Name'].unique())
    selected_players = players[:] if selected_player == 'All' else [selected_player]

    # Filter matchdays_df for the selected matchday or up to the selected matchday
    filtered_matchdays_df = matchdays_df[matchdays_df['Matchday'] <= matchday]

    section = st.session_state.get('selected_analysis_section', 'Pie Chart')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Pie Chart", key="button_pie_chart"):
            section = "Pie Chart"
    with col2:
        if st.button("Confusion Matrix", key="button_confusion_matrix"):
            section = "Confusion Matrix"
    with col3:
        if st.button("Heat Map", key="button_heat_map"):
            section = "Heat Map"
    with col4:
        if st.button("Line Plot", key="button_line_plot"):
            section = "Line Plot"

    st.session_state['selected_analysis_section'] = section

    # Pass the filtered matchdays_df to the chart functions
    if section == "Pie Chart":
        display_group_pie_chart(filtered_matchdays_df, selected_players)
        if st.button("Generate Analysis", key="generate_analysis_pie_chart"):
            analysis = generate_pie_chart_analysis(selected_players, filtered_matchdays_df)
            if analysis:
                st.markdown(analysis)
    elif section == "Confusion Matrix":
        display_confusion_matrix(filtered_matchdays_df, selected_players, matchday)
        if st.button("Generate Analysis", key="generate_analysis_confusion_matrix"):
            analysis = generate_confusion_matrix_analysis(selected_players, filtered_matchdays_df, matchday)
            if analysis:
                st.markdown(analysis)
    elif section == "Heat Map":
        display_group_heat_map(filtered_matchdays_df, selected_players)
        if st.button("Generate Analysis", key="generate_analysis_heat_map"):
            analysis = generate_heat_map_analysis(selected_players, filtered_matchdays_df)
            if analysis:
                st.markdown(analysis)
    elif section == "Line Plot":
        display_line_plot(filtered_matchdays_df, selected_players, matchday)
        if st.button("Generate Analysis", key="generate_analysis_line_plot"):
            analysis = generate_line_plot_analysis(selected_players, filtered_matchdays_df, matchday)
            if analysis:
                st.markdown(analysis)