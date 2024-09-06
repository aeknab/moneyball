import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Define the color palette for each player
color_palette = {
    "Andreas": "rgba(102, 194, 165, 0.75)",  # light green
    "Gerd": "rgba(252, 141, 98, 0.75)",      # light orange
    "Geri": "rgba(141, 160, 203, 0.75)",     # light blue
    "Hermann": "rgba(231, 138, 195, 0.75)",  # light pink
    "Johnny": "rgba(166, 216, 84, 0.75)",    # light lime green
    "Moddy": "rgba(255, 217, 47, 0.75)",     # light yellow
    "Samson": "rgba(229, 196, 148, 0.75)"    # light brown
}

# Function to display the stacked bar plot
def display_stacked_bar_chart(rankings_df, matchday, selected_player):
    st.subheader("Group Points per Matchday")

    # Filter the data for matchdays up to the selected matchday
    filtered_rankings_df = rankings_df[rankings_df['Spieltag'] <= matchday]

    # Calculate the total points for each matchday
    matchday_totals = filtered_rankings_df.groupby(['Spieltag', 'Name'])['Punkte'].sum().unstack(fill_value=0)
    
    # Sort players alphabetically for consistent ordering in the stacked bars
    matchday_totals = matchday_totals.reindex(sorted(matchday_totals.columns), axis=1)

    # Find the maximum combined points scored by the group in any matchday
    max_combined_points = matchday_totals.sum(axis=1).max()

    # Create a plotly figure
    fig = go.Figure()

    if selected_player == 'All':
        # Stacked bar plot for all players
        for player in matchday_totals.columns:
            fig.add_trace(go.Bar(
                x=matchday_totals.index,
                y=matchday_totals[player],
                name=player,
                marker=dict(color=color_palette.get(player, 'rgba(179, 179, 179, 0.75)')),
                hovertemplate=f"<b>{player}</b><br>Points: {{y}}<extra></extra>",
                showlegend=False  # Disable individual player legend when "All" is selected
            ))

        # Calculate the season average
        season_avg = matchday_totals.sum(axis=1).mean()

        # Add the season average line (white dashed line)
        fig.add_trace(go.Scatter(
            x=matchday_totals.index,
            y=[season_avg] * 34,  # Ensure this is for all 34 matchdays
            mode="lines",
            name=f"Season Avg: {season_avg:.1f}",
            line=dict(color="white", width=2, dash="dot"),
        ))

    else:
        # Single player bar plot
        fig.add_trace(go.Bar(
            x=matchday_totals.index,
            y=matchday_totals[selected_player],
            name=selected_player,
            marker=dict(color=color_palette[selected_player]),
            hovertemplate=f"<b>{selected_player}</b><br>Points: {{y}}<extra></extra>",
            showlegend=False  # Disable individual player legend
        ))

        # Calculate the player's season average
        player_avg = matchday_totals[selected_player].mean()

        # Calculate the group's season average excluding the selected player
        remaining_players_count = matchday_totals.shape[1] - 1  # Total players minus the selected player
        group_avg_excluding_player = matchday_totals.drop(columns=selected_player).sum(axis=1).mean() / remaining_players_count

        # Add player average line (blue dotted line)
        fig.add_trace(go.Scatter(
            x=matchday_totals.index,
            y=[player_avg] * 34,
            mode="lines",
            name=f"{selected_player}'s Avg: {player_avg:.1f}",
            line=dict(color="blue", width=2, dash="dot"),
        ))

        # Add group average line excluding the selected player (white dotted line)
        fig.add_trace(go.Scatter(
            x=matchday_totals.index,
            y=[group_avg_excluding_player] * 34,
            mode="lines",
            name=f"Group Avg (excluding {selected_player}): {group_avg_excluding_player:.1f}",
            line=dict(color="white", width=2, dash="dot"),
        ))

    # Add the midpoint of the season (dotted line between matchdays 17 and 18)
    fig.add_vline(x=17.5, line=dict(color="grey", width=1, dash="dot"))

    # Set axis ranges
    fig.update_layout(
        title="Group Points per Matchday",
        xaxis=dict(title="Matchday", range=[0.5, 34.5], tickmode="linear"),  # Extend the x-axis from 0.5 to 34.5
        yaxis=dict(title="Points", range=[0, max(21, max_combined_points)] if selected_player == 'All' else [0, 21]),  # Set max for y-axis
        barmode="stack",
        template="plotly_white",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        height=600,
        width=800,
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)