import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Define the color palette
color_palette = {
    "Andreas": "rgba(102, 194, 165, 0.85)",  # light green
    "Gerd": "rgba(252, 141, 98, 0.85)",      # light orange
    "Geri": "rgba(141, 160, 203, 0.85)",     # light blue
    "Hermann": "rgba(231, 138, 195, 0.85)",  # light pink
    "Johnny": "rgba(166, 216, 84, 0.85)",    # light lime green
    "Moddy": "rgba(255, 217, 47, 0.85)",     # light yellow
    "Samson": "rgba(229, 196, 148, 0.85)",   # light brown
    "Gray": "rgba(179, 179, 179, 0.85)"      # light gray for other players when a single player is selected
}

def adjust_color_opacity(color, opacity):
    """Adjust the opacity of an RGBA color string."""
    rgba = color.strip('rgba()').split(',')
    return f'rgba({rgba[0]}, {rgba[1]}, {rgba[2]}, {opacity})'

def display_group_bump_chart(matchday, rankings_df, selected_players):
    st.subheader("Bump Chart")

    # Filter rankings data up to and including the selected matchday
    filtered_rankings_df = rankings_df[(rankings_df['Spieltag'] <= matchday)]

    # Create a pivot table with players as rows and matchdays as columns, with rank as values
    rank_pivot = filtered_rankings_df.pivot(index='Name', columns='Spieltag', values='Rang')

    # Create a Plotly figure
    fig = go.Figure()

    # Add a trace for each player
    for player in rank_pivot.index:
        line_color = color_palette.get(player, 'rgba(102, 194, 165, 0.75)')
        line_width = 2

        # If a specific player is selected, highlight their line
        if len(selected_players) == 1 and selected_players[0] != 'All':
            if player == selected_players[0]:
                line_color = adjust_color_opacity(line_color, 1.0)  # Highlight selected player's line
                line_width = 3
            else:
                line_color = adjust_color_opacity(color_palette["Gray"], 0.85)  # Grey out other players

        fig.add_trace(go.Scatter(
            x=rank_pivot.columns,
            y=rank_pivot.loc[player],
            mode='lines+markers',
            name=player,
            marker=dict(size=8, color=line_color),
            line=dict(width=line_width, color=line_color)
        ))

    # Customize the layout
    fig.update_layout(
        title_text=f'Group Player Rankings - Bump Chart (up to Matchday {matchday})',
        xaxis=dict(
            title='Matchday',
            tickmode='linear',
            tick0=1,
            dtick=1,
            range=[0, 35],  # Static x-axis from 0 to 34
            showgrid=True,
            tickvals=list(range(1, 36)),
            ticktext=list(range(1, 36))
        ),
        yaxis=dict(
            title='Rank',
            autorange='reversed',
            dtick=1,
            showgrid=True
        ),
        template='plotly_white',
        height=600,
        width=1000,
        margin=dict(l=50, r=20, t=50, b=50),
        showlegend=True
    )

    # Add a vertical dotted line for the winter break (between matchday 17 and 18)
    fig.add_vline(x=17.5, line=dict(color='rgba(255, 255, 255, 0.5)', dash='dot', width=1.5))

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
