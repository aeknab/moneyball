import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from io import BytesIO
import base64

# Import necessary functions from other modules
from groups.season.group_table import display_group_table  # This is the Bar Chart
from groups.season.bump_chart_group import display_group_bump_chart
from groups.season.donut_chart import display_donut_chart
from groups.season.histogram_group import display_matchday_histogram
from groups.season.density_plot import display_season_density_plot
#from groups.season.crosstable_group import display_player_crosstable_view  # Import the crosstable function

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

# Utility function to convert an image to base64 for Plotly
def image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str

def display_group_table_with_highlight(matchday, rankings_df, selected_player):
    # Filter and sort the DataFrame by matchday and total points in descending order
    filtered_df = rankings_df[rankings_df['Spieltag'] == matchday]
    filtered_df = filtered_df.sort_values('Gesamtpunkte', ascending=False)

    # Reverse the DataFrame to align it with the color assignment
    filtered_df = filtered_df.iloc[::-1]

    # Determine bar colors based on the selected player
    if selected_player == 'All':
        bar_colors = [color_palette[player] for player in filtered_df['Name']]
    else:
        bar_colors = [color_palette["Gray"] if player != selected_player else color_palette[selected_player] for player in filtered_df['Name']]

    # Create the horizontal bar chart using Plotly
    fig = go.Figure()

    max_points = filtered_df['Gesamtpunkte'].max()

    for player, points in zip(filtered_df['Name'], filtered_df['Gesamtpunkte']):
        fig.add_trace(go.Bar(
            x=[points],
            y=[player],
            orientation='h',
            marker=dict(color=color_palette.get(player, 'rgba(102, 194, 165, 0.85)')),
            showlegend=False
        ))

        # Add player logos next to the bars
        player_logo_path = f"data/logos/groups/{player}.png"  # Ensure the path to the player logos is correct
        player_logo = Image.open(player_logo_path)
        player_logo_resized = player_logo.resize((40, 40))  # Resize the logo
        logo_base64 = image_to_base64(player_logo_resized)

        # Position the logo to the right of the bar
        fig.add_layout_image(
            dict(
                source=f'data:image/png;base64,{logo_base64}',
                xref="x", yref="y",
                x=points + max_points * 0.05,  # Adjust the position to be slightly right of the bar
                y=player,
                sizex=40 / max_points,  # Adjust size to match bar height
                sizey=0.5,
                xanchor="left",
                yanchor="middle",
                layer="above"
            )
        )

    fig.update_layout(
        title_text="Bar Chart",  # Adding a title to the Bar Chart
        xaxis_title="Total Points",
        yaxis_title="Players",
        height=400,
        width=600,
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

def display_season_section(matchday, rankings_df, matchdays_df):
    # Add a dropdown to select a player
    players = sorted(rankings_df['Name'].unique())
    players.insert(0, 'All')  # Add 'All' option at the beginning
    selected_player = st.selectbox("Select Player", players)  # Use a dropdown for player selection

    # Ensure selected_player is always a list
    if selected_player == 'All':
        selected_players = rankings_df['Name'].unique().tolist()
    else:
        selected_players = [selected_player]

    # Filter by the selected matchday
    filtered_df = rankings_df[rankings_df["Spieltag"] == matchday]

    # Sort by Rank
    sorted_df = filtered_df.sort_values(by="Rang")

    # Add rank change information
    if matchday > 1:
        previous_matchday = matchday - 1
        previous_df = rankings_df[rankings_df["Spieltag"] == previous_matchday]

        merged_df = pd.merge(
            sorted_df[['Name', 'Rang']],
            previous_df[['Name', 'Rang']],
            on='Name',
            suffixes=('', '_previous'),
            how='left'
        )

        merged_df['Rank Change'] = merged_df.apply(
            lambda row: '⬆️' if row['Rang'] < row['Rang_previous'] else ('⬇️' if row['Rang'] > row['Rang_previous'] else '⏺️'),
            axis=1
        )

        sorted_df = pd.merge(sorted_df, merged_df[['Name', 'Rank Change']], on='Name', how='left')
    else:
        sorted_df['Rank Change'] = '--'

    sorted_df['MD Winner'] = sorted_df['Spieltagssieger'].apply(
        lambda x: f"🏆{x:.1f}" if x > 0 and x < 1 else ('🏆' if x == 1 else '')
    )

    sorted_df['MD Wins'] = sorted_df['Gesamtspieltagssiege'].apply(
        lambda x: f"x {x}" if x > 0 else ''
    )

    if matchday == 34:
        sorted_df['Total Points'] = sorted_df.apply(
            lambda row: f"🥇 {row['Gesamtpunkte']}" if row['Rang'] == 1 else (
                        f"🥈 {row['Gesamtpunkte']}" if row['Rang'] == 2 else (
                        f"🥉 {row['Gesamtpunkte']}" if row['Rang'] == 3 else str(row['Gesamtpunkte']))),
            axis=1
        )
    else:
        sorted_df['Total Points'] = sorted_df['Gesamtpunkte']

    overview_data = sorted_df[["Rang", "Rank Change", "Name", "Punkte", "MD Winner", "MD Wins", "Total Points"]]
    overview_data.columns = ["Rank", "+/-", "Name", "Matchday Points", "MD Winner", "MD Wins", "Total Points"]

    # Table creation with row highlighting
    table_html = """
    <style>
    .styled-table {
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        font-family: 'Sans-serif', Arial, Helvetica, sans-serif;
        width: 100%;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
        border-radius: 15px;
        overflow: hidden;
        background-color: rgba(255, 255, 255, 0.5);
        border: 2px solid #696969;
    }
    .styled-table thead tr {
        background-color: rgba(14, 17, 23, 0.70);
        color: #ffffff;
        text-align: left;
    }
    .styled-table th,
    .styled-table td {
        padding: 12px 15px;
        text-align: center;
    }
    .styled-table tbody tr {
        background-color: rgba(14, 17, 23, 0.35);
        border-bottom: 1px solid rgba(97, 101, 114, 0.9);
    }
    .styled-table tbody tr:last-of-type {
        border-bottom: 2px solid rgba(97, 101, 114, 0.9);
    }
    </style>
    <table class="styled-table">
    <thead>
        <tr>
            <th>Rank</th>
            <th>↕️</th>
            <th>Name</th>
            <th>Matchday Points</th>
            <th>MD Winner</th>
            <th>MD Wins</th>
            <th>Total Points</th>
        </tr>
    </thead>
    <tbody>
    """

    for _, row in overview_data.iterrows():
        row_color = f"background-color: {color_palette[row['Name']]};" if row['Name'] == selected_player else ""
        table_html += f"<tr style='{row_color}'><td>{row['Rank']}</td><td>{row['+/-']}</td><td>{row['Name']}</td><td>{row['Matchday Points']}</td><td>{row['MD Winner']}</td><td>{row['MD Wins']}</td><td>{row['Total Points']}</td></tr>"

    table_html += "</tbody></table>"

    # Display the Group Table only once
    st.markdown(table_html, unsafe_allow_html=True)

    # Histogram (Second)
    display_matchday_histogram(matchday, rankings_df, selected_players=selected_players)

    # Density Plot (Third)
    display_season_density_plot(matchday, rankings_df, selected_players)

    # Bump Chart (Fifth)
    display_group_bump_chart(matchday, rankings_df, selected_players)

    # Bar Chart (Sixth)
    display_group_table_with_highlight(matchday, rankings_df, selected_player)
    
    # Donut Chart (Fourth)
    display_donut_chart(matchdays_df, selected_players, matchday)

    # Display Crosstable only if a specific player is selected
    #if selected_player != 'All':
    #    st.subheader(f"Crosstable for {selected_player}")
    #    display_player_crosstable_view(rankings_df, selected_player, matchday)

def display_matchday_histogram(matchday, rankings_df, selected_players):
    # Filter data for the selected matchday
    filtered_df = rankings_df[(rankings_df['Spieltag'] == matchday)]

    # Sort players by points for the matchday
    filtered_df = filtered_df.sort_values('Punkte', ascending=False)

    # Extract the points scored by each player
    points = filtered_df['Punkte']
    players = filtered_df['Name']

    # Determine bar colors
    if len(selected_players) == 1 and selected_players[0] != 'All':
        # If a single player is selected, gray out the other players
        bar_colors = [color_palette[player] if player in selected_players else color_palette["Gray"] for player in players]
    else:
        # If "All" is selected, use the normal colors
        bar_colors = [color_palette[player] for player in players]

    # Calculate average points for the matchday
    matchday_avg = points.mean()

    # Calculate the total points scored up to the selected matchday
    total_points = rankings_df[(rankings_df['Spieltag'] <= matchday)]['Punkte'].sum()

    # Calculate the number of matchdays up to the selected matchday
    num_matchdays = matchday 

    # Calculate the number of players
    num_players = len(players)

    # Calculate the Season Average
    season_avg = total_points / (num_matchdays * num_players)

    # Create the histogram using Plotly
    fig = go.Figure()

    # Add bars for each player
    fig.add_trace(go.Bar(
        x=players,
        y=points,
        marker=dict(color=bar_colors),
        hovertemplate='<b>Points:</b> %{y}<br><b>MD Rank:</b> %{customdata[0]}<extra></extra>',
        customdata=[(i+1,) for i in range(len(players))],  # Add rank information
        showlegend=False  # Hide this trace from the legend
    ))

    # Add dotted lines for matchday and season averages
    fig.add_trace(go.Scatter(
        x=[players.iloc[0], players.iloc[-1]],  # Ensure the lines span the entire width of the bars
        y=[matchday_avg, matchday_avg],
        mode="lines",
        name=f"Matchday Avg: {matchday_avg:.1f}",
        line=dict(color="blue", width=2, dash="dot"),
        showlegend=True
    ))

    fig.add_trace(go.Scatter(
        x=[players.iloc[0], players.iloc[-1]],  # Ensure the lines span the entire width of the bars
        y=[season_avg, season_avg],
        mode="lines",
        name=f"Season Avg: {season_avg:.1f}",
        line=dict(color="white", width=2, dash="dot"),
        showlegend=True
    ))

    # Update layout with adjusted standoff and legend position
    fig.update_layout(
        title_text=f"Distribution of Points Scored in Season",
        xaxis_title="Players",
        yaxis_title="Points",
        yaxis=dict(
            autorange=True,
            title_standoff=10,  # Standoff for y-axis
        ),
        xaxis=dict(
            tickangle=15,
            title_standoff=5,  # Further reduced standoff for x-axis
        ),
        barmode="group",
        height=400,
        width=600,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,  # Push the legend down slightly
            xanchor="center",
            x=0.5
        )
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)