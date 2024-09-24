# ChatGPT/summaries.py

from openai import OpenAI
import pandas as pd
import streamlit as st

client = OpenAI(api_key="sk-o0hrLU1sy_khDaVw-sFP1pnIOP-SLylV1lC-gaOgLWT3BlbkFJ7b2I0vPST6fT6vgTB90vaf-DIDxpOg00Z8ax3cOhIA")

def generate_summary_prompt(matchday_data, group_name, rankings):
    prompt = f"""
    Just the Facts: Recap of Matchday {matchday_data['Matchday'].iloc[0]} for the prediction group "{group_name}"
    
    Participants and their points:
    """
    for index, row in rankings.iterrows():
        prompt += f"{row['Rang']}. {row['Name']} - {row['Gesamtpunkte']} points\n"

    prompt += "\nMatch results and predictions:\n"
    for _, row in matchday_data.iterrows():
        prompt += f"{row['Home Team']} {row['Home Goals']}:{row['Away Goals']} {row['Away Team']}\n"
        for player in ['Andreas', 'Gerd', 'Geri', 'Hermann', 'Johnny', 'Moddy', 'Samson']:
            prompt += f"{player}: {row[f'{player} Home Goals Predicted']}:{row[f'{player} Away Goals Predicted']} Points: {row['Result']}\n"

    prompt += "\nPlease generate a summary for this matchday."
    return prompt

def generate_summary(matchday_data, group_name, rankings):
    prompt = generate_summary_prompt(matchday_data, group_name, rankings)
    try:
        response = client.chat.completions.create(model="gpt-4",  # Use GPT-4 for better quality responses
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0.7)
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"An error occurred while generating the summary: {e}")
        return None
