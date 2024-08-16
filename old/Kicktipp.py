import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the datasets
matchdays_df = pd.read_csv('data/merged_matchdays.csv')
rankings_df = pd.read_csv('data/merged_rankings.csv')

# Set up the page content
st.header("Kicktipp Predictions")

# Layout for Matchday and Player selection
col1, col2 = st.columns(2)

with col1:
    # Filter by Matchday
    matchdays = sorted(rankings_df['Matchday'].unique(), reverse=True)
    selected_matchday = st.selectbox("Matchday", matchdays)

with col2:
    # Filter by Player
    players = sorted(rankings_df['Name'].unique())
    players.insert(0, 'All')  # Add 'All' option at the beginning

    selected_players = st.multiselect("Player(s)", players, default=['All'])

    if 'All' in selected_players:
        selected_players = players[1:]  # Select all players if 'All' is selected

# Section 1: Group Table
st.subheader("Group Table")

# Filter rankings data up to and including the selected matchday
filtered_rankings_df = rankings_df[(rankings_df['Matchday'] <= selected_matchday) & (rankings_df['Name'].isin(selected_players))]

# Calculate the total points for each player up to and including the selected matchday
player_points = filtered_rankings_df.groupby('Name')['Punkte'].sum().reindex(selected_players)

# Sort the players by their total points
player_points = player_points.sort_values(ascending=False)

# Plot the league table
plt.style.use('fivethirtyeight')
fig, ax = plt.subplots(figsize=(10, 6))

ax.barh(player_points.index, player_points.values, color='#1f77b4')

ax.set_xlabel('Points')
ax.set_ylabel('Players')
ax.set_title(f'Kicktipp League Table - Matchday {selected_matchday}')

# Invert y-axis to have the top player at the top
ax.invert_yaxis()

# Display the chart in Streamlit
st.pyplot(fig)

# Section 2: Bump Chart
st.subheader("Bump Chart")

# Create a pivot table with players as rows and matchdays as columns, with rank as values
rank_pivot = filtered_rankings_df.pivot(index='Name', columns='Matchday', values='Rang')

# Plot the bump chart
plt.style.use('fivethirtyeight')
fig, ax = plt.subplots(figsize=(12, 8))

for player in rank_pivot.index:
    ax.plot(rank_pivot.columns, rank_pivot.loc[player], marker='o', label=player)

# Customize the chart
ax.set_xlim(rank_pivot.columns.min(), rank_pivot.columns.max())
ax.set_ylim(1, len(rank_pivot) + 1)
ax.invert_yaxis()  # Invert y-axis to show rank 1 at the top
ax.set_yticks(range(1, len(rank_pivot) + 1))
ax.set_yticklabels(range(1, len(rank_pivot) + 1))
ax.set_xticks(rank_pivot.columns)
ax.set_xticklabels(rank_pivot.columns)
ax.set_xlabel('Matchday')
ax.set_ylabel('Rank')
ax.set_title(f'Kicktipp Player Rankings - Bump Chart (up to Matchday {selected_matchday})')

ax.legend(loc='upper left', bbox_to_anchor=(1, 1), title='Players')

# Display the chart in Streamlit
st.pyplot(fig)

# Plotting setup for side-by-side heatmaps
heatmap_col1, heatmap_col2 = st.columns(2)

# Heatmap for Kicktipp Predictions
with heatmap_col1:
    st.subheader("Kicktipp Predictions Heatmap")
    
    # Initialize a dataframe to accumulate the counts of each home-away goal combination
    goal_combinations = pd.DataFrame(0, index=range(7), columns=range(7))
    
    for player in selected_players:
        home_col = f'{player} Home Goals Predicted'
        away_col = f'{player} Away Goals Predicted'
        
        # Count occurrences of each home-away goal combination
        counts = matchdays_df.groupby([home_col, away_col]).size()
        
        # Add these counts to the goal_combinations dataframe
        for (home_goals, away_goals), count in counts.items():
            if home_goals <= 6 and away_goals <= 6:  # Consider only goals from 0 to 6
                goal_combinations.at[home_goals, away_goals] += count

    # Plot the heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(goal_combinations, annot=True, cmap='viridis', cbar=True, linewidths=0.5, annot_kws={"size": 10}, fmt="d")
    plt.title("Kicktipp Predictions Heatmap")
    plt.xlabel("Away Goals")
    plt.ylabel("Home Goals")
    plt.gca().invert_yaxis()  # Invert y-axis to have 0 at the bottom
    
    st.pyplot(plt)

# Heatmap for Bundesliga Actual Results
with heatmap_col2:
    st.subheader("Bundesliga Actual Results Heatmap")
    
    # Initialize a dataframe to accumulate the counts of each home-away goal combination
    goal_combinations_actual = pd.DataFrame(0, index=range(7), columns=range(7))
    
    home_goals = matchdays_df['Home Goals']
    away_goals = matchdays_df['Away Goals']
    
    # Count occurrences of each home-away goal combination
    for h_goal, a_goal in zip(home_goals, away_goals):
        h_index = h_goal if h_goal < 6 else 6
        a_index = a_goal if a_goal < 6 else 6
        goal_combinations_actual.at[h_index, a_index] += 1

    # Rename the last index to '6+'
    goal_combinations_actual.index = goal_combinations_actual.index.astype(str)
    goal_combinations_actual.columns = goal_combinations_actual.columns.astype(str)
    goal_combinations_actual.rename(index={'6': '6+'}, columns={'6': '6+'}, inplace=True)

    # Plot the heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(goal_combinations_actual, annot=True, cmap='viridis', cbar=True, linewidths=0.5, annot_kws={"size": 10}, fmt="d")
    plt.title("Bundesliga Actual Match Results Heatmap")
    plt.xlabel("Away Goals")
    plt.ylabel("Home Goals")
    plt.gca().invert_yaxis()  # Invert y-axis to have 0 at the bottom
    
    st.pyplot(plt)

# Section 3: Pie Charts for Predictions and Actual Results
st.subheader("Pie Charts: Kicktipp Predictions vs. Bundesliga Actual Results")

# Aggregate predictions for all selected players
predictions = {
    'Home Win': 0,
    'Tie': 0,
    'Away Win': 0
}

for player in selected_players:
    result_col = f'{player} Result Predicted'
    player_results = matchdays_df[result_col]
    
    predictions['Home Win'] += player_results[player_results == 'Home Win'].count()
    predictions['Tie'] += player_results[player_results == 'Tie'].count()
    predictions['Away Win'] += player_results[player_results == 'Away Win'].count()

# Aggregate actual Bundesliga results
results = {
    'Home Win': 0,
    'Tie': 0,
    'Away Win': 0
}

results['Home Win'] = matchdays_df['Result'][matchdays_df['Result'] == 'Home Win'].count()
results['Tie'] = matchdays_df['Result'][matchdays_df['Result'] == 'Tie'].count()
results['Away Win'] = matchdays_df['Result'][matchdays_df['Result'] == 'Away Win'].count()

# Set up the layout for side-by-side pie charts
pie_col1, pie_col2 = st.columns(2)

# Pie chart for Kicktipp Predictions
with pie_col1:
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(predictions.values(), labels=predictions.keys(), autopct='%1.1f%%', startangle=90)
    ax.set_title('Kicktipp Predictions: Wins, Ties, Losses')
    st.pyplot(fig)

# Pie chart for Bundesliga Actual Results
with pie_col2:
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(results.values(), labels=results.keys(), autopct='%1.1f%%', startangle=90)
    ax.set_title('Bundesliga Actual Results: Wins, Ties, Losses')
    st.pyplot(fig)

