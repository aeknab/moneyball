import streamlit as st
import pandas as pd
from analysis.pie_chart_group import display_group_pie_chart, calculate_pie_chart_data
from analysis.heat_map_group import display_group_heat_map, calculate_heat_map_data
from analysis.confusion_matrix import display_confusion_matrix, calculate_confusion_matrix_data
from analysis.line_plot import display_line_plot, calculate_line_plot_data
from chatgpt.prompt_pie_chart import pie_chart_prompt_template
from chatgpt.prompt_confusion_matrix import confusion_matrix_prompt_template
from chatgpt.prompt_heatmap import heat_map_prompt_template
from chatgpt.prompt_line_plot import line_plot_prompt_template
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
    data = calculate_confusion_matrix_data(matchdays_df, selected_players, matchday)
    prompt = confusion_matrix_prompt_template.format(
        player_name=selected_players if selected_players != 'All' else 'All players',
        accuracy=(data['confusion_matrix'].trace() / data['confusion_matrix'].sum()) * 100
    )
    return generate_analysis(prompt)

def generate_heat_map_analysis(selected_players, matchdays_df):
    data = calculate_heat_map_data(matchdays_df, selected_players)
    prompt = heat_map_prompt_template.format(
        player_name=selected_players if selected_players != 'All' else 'All players',
        most_frequent_score=f"{data['most_frequent_score'][0]}-{data['most_frequent_score'][1]}"
    )
    return generate_analysis(prompt)

def generate_line_plot_analysis(selected_players, matchdays_df):
    data = calculate_line_plot_data(matchdays_df, selected_players)
    prompt = line_plot_prompt_template.format(
        player_name=selected_players if selected_players != 'All' else 'All players',
        avg_predicted_goals=data['avg_predicted_goals'],
        avg_actual_goals=data['avg_actual_goals'],
        prediction_accuracy=calculate_prediction_accuracy(data['group_predicted_goals'], data['actual_goals'])
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

def display_analysis_section(matchday, rankings_df, matchdays_df):
    col1 = st.columns(1)[0]
    with col1:
        players = sorted(rankings_df['Name'].unique())
        players.insert(0, 'All')
        selected_player = st.selectbox("Select Player", players)
    
    selected_players = players[1:] if selected_player == 'All' else [selected_player]

    section = st.session_state.get('selected_analysis_section', 'Pie Chart')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Pie Chart"):
            section = "Pie Chart"
    with col2:
        if st.button("Confusion Matrix"):
            section = "Confusion Matrix"
    with col3:
        if st.button("Heat Map"):
            section = "Heat Map"
    with col4:
        if st.button("Line Plot"):
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