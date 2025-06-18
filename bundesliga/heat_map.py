import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# Function to filter matches based on the selected season and matchday
def filter_matches_for_season(df, selected_season, matchday):
    if selected_season == '2023/24':
        # Exclude data from the selected matchday for the 2023/24 season
        return df[(df['Season'] == selected_season) & (df['Matchday'] < matchday)]
    else:
        # Include data from the selected matchday for previous seasons (2005/06 to 2022/23)
        return df[(df['Season'] == selected_season) & (df['Matchday'] <= matchday)]

def plot_heatmap(matchdays_df, selected_matchday):
    st.subheader("Bundesliga Actual Results Heatmap")
    
    # Filter the data to include only matchdays before or up to the selected matchday, depending on the season
    matchdays_df = filter_matches_for_season(matchdays_df, matchdays_df['Season'].iloc[0], selected_matchday)
    
    # Identify the highest number of goals scored in a single game by any team
    max_goals = max(matchdays_df['Home Goals'].max(), matchdays_df['Away Goals'].max())

    # Adjust the maximum value to be used on the axes (both x and y)
    max_value = max_goals

    # Initialize a dataframe to accumulate the counts of each home-away goal combination
    goal_combinations_actual = pd.DataFrame(0, index=range(max_value + 1), columns=range(max_value + 1))
    
    home_goals = matchdays_df['Home Goals']
    away_goals = matchdays_df['Away Goals']
    
    # Count occurrences of each home-away goal combination
    for h_goal, a_goal in zip(home_goals, away_goals):
        goal_combinations_actual.at[h_goal, a_goal] += 1

    # Convert index and columns to strings for labeling
    goal_combinations_actual.index = goal_combinations_actual.index.astype(str)
    goal_combinations_actual.columns = goal_combinations_actual.columns.astype(str)
    
    # Create the heatmap using Plotly
    fig = go.Figure(data=go.Heatmap(
        z=goal_combinations_actual.values,
        x=goal_combinations_actual.columns,
        y=goal_combinations_actual.index,
        colorscale='Viridis',
        showscale=False,
        text=goal_combinations_actual.values,
        texttemplate="%{text}",  # Display the values in the heatmap cells
        hovertemplate="Home Goals: %{y}<br>Away Goals: %{x}<br>Count: %{z}<extra></extra>"
    ))

    # Update the layout to match your requirements
    fig.update_layout(
        title="Bundesliga Actual Match Results Heatmap",
        xaxis=dict(
            title="Away Goals",
            range=[-0.5, max_value + 0.5],  # Ensure axis length matches the maximum value
            scaleanchor="y",  # Ensure x and y axes are equal in length
            constrain="domain",
            tickmode="linear",  # Ensure that each tick is labeled
            dtick=1,  # Label each tick (0, 1, 2, etc.)
        ),
        yaxis=dict(
            title="Home Goals",
            range=[-0.5, max_value + 0.5],  # Ensure axis length matches the maximum value
            tickmode="linear",  # Ensure that each tick is labeled
            dtick=1,  # Label each tick (0, 1, 2, etc.)
        ),
        height=600,
        width=600  # Ensure square layout
    )

    st.plotly_chart(fig)

def display_heat_map(df, selected_season, selected_matchday):
    # Plot the static heatmap
    plot_heatmap(df[df['Season'] == selected_season], selected_matchday)
