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
        
        # Assuming these are the correct percentages you want to use
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

    # Use the first selected player as the player_name, or a generic 'All Players' if multiple are selected
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

    # Use the first selected player as the player_name, or a generic 'All Players' if multiple are selected
    player_name = selected_players[0] if len(selected_players) == 1 else "All Players"

    # Format the prompt with the retrieved data
    prompt = heat_map_prompt_template.format(
        player_name=player_name,
        hot_zone_success_rate=hot_zone_success_rate,
        most_frequent_score=most_frequent_score_str
    )

    return generate_analysis(prompt)

def generate_line_plot_analysis(selected_players, matchdays_df):
    # Calculate line plot data and get the trend
    data = calculate_line_plot_data(matchdays_df, selected_players)

    # Access the trend data from the returned dictionary
    trend_over_time = data["trend_over_time"]
    trend_description = data["trend_description"]

    # Use the trend data to generate the analysis
    player_name = selected_players[0] if len(selected_players) == 1 else "All Players"
    
    prompt = line_plot_prompt_template.format(
        player_name=player_name,
        trend_over_time=trend_over_time,
        trend_description=trend_description
    )

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
    selected_players = players[1:] if selected_player == 'All' else [selected_player]

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

    if section == "Pie Chart":
        display_group_pie_chart(matchdays_df, selected_players)
        if st.button("Generate Analysis", key="generate_analysis_pie_chart"):
            analysis = generate_pie_chart_analysis(selected_players, matchdays_df)
            if analysis:
                st.markdown(analysis)
    elif section == "Confusion Matrix":
        display_confusion_matrix(matchdays_df, selected_players, matchday)
        if st.button("Generate Analysis", key="generate_analysis_confusion_matrix"):
            analysis = generate_confusion_matrix_analysis(selected_players, matchdays_df, matchday)
            if analysis:
                st.markdown(analysis)
    elif section == "Heat Map":
        display_group_heat_map(matchdays_df, selected_players)
        if st.button("Generate Analysis", key="generate_analysis_heat_map"):
            analysis = generate_heat_map_analysis(selected_players, matchdays_df)
            if analysis:
                st.markdown(analysis)
    elif section == "Line Plot":
        display_line_plot(matchdays_df, selected_players)
        if st.button("Generate Analysis", key="generate_analysis_line_plot"):
            analysis = generate_line_plot_analysis(selected_players, matchdays_df)
            if analysis:
                st.markdown(analysis)