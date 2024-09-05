import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from io import BytesIO
import base64

# Import necessary functions from other modules
from groups.season.bump_chart_group import display_bump_chart_group, animate_bump_chart_group
from groups.season.bar_chart_group import create_group_table_animation
from groups.season.donut_chart import display_donut_chart
from groups.season.histogram_group import display_matchday_histogram
from groups.season.density_plot import display_season_density_plot

# Define the color palette
color_palette = {
    "Andreas": "rgba(102, 194, 165, 0.85)",
    "Gerd": "rgba(252, 141, 98, 0.85)",
    "Geri": "rgba(141, 160, 203, 0.85)",
    "Hermann": "rgba(231, 138, 195, 0.85)",
    "Johnny": "rgba(166, 216, 84, 0.85)",
    "Moddy": "rgba(255, 217, 47, 0.85)",
    "Samson": "rgba(229, 196, 148, 0.85)",
    "Gray": "rgba(179, 179, 179, 0.85)"  # Default color for other players
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
        bar_colors = [color_palette.get(player, color_palette["Gray"]) for player in filtered_df['Name']]
    else:
        bar_colors = [color_palette["Gray"] if player != selected_player else color_palette.get(selected_player, color_palette["Gray"]) for player in filtered_df['Name']]

    # Create the horizontal bar chart using Plotly
    fig = go.Figure()

    max_points = filtered_df['Gesamtpunkte'].max()

    for player, points, color in zip(filtered_df['Name'], filtered_df['Gesamtpunkte'], bar_colors):
        fig.add_trace(go.Bar(
            x=[points],
            y=[player],
            orientation='h',
            marker=dict(color=color),
            showlegend=False
        ))

        # Add player logos next to the bars
        player_logo_path = f"data/logos/groups/{player}.png"
        player_logo = Image.open(player_logo_path)
        player_logo_resized = player_logo.resize((50, 50))
        logo_base64 = image_to_base64(player_logo_resized)

        fig.add_layout_image(
            dict(
                source=f'data:image/png;base64,{logo_base64}',
                xref="x", yref="y",
                x=points + max_points * 0.05,
                y=player,
                sizex=50 / max_points,
                sizey=0.5,
                xanchor="left",
                yanchor="middle",
                layer="above"
            )
        )

    fig.update_layout(
        title_text="Bar Chart",
        xaxis_title="Total Points",
        yaxis_title="Players",
        height=400,
        width=600,
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

def display_season_section(matchday, rankings_df, matchdays_df, selected_player):
    # Ensure selected_player is always a list for proper handling
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

    # Add player faces to the left of their names, with adjusted size and alignment
    # for i in range(len(overview_data)):
    #     player_name = overview_data.loc[i, 'Name'].strip("<b>").strip("</b>")
    #     player_logo_path = f"data/logos/groups/{player_name}.png"
    #     try:
    #         player_logo_base64 = image_to_base64(Image.open(player_logo_path))
    #         overview_data.loc[i, 'Name'] = f"<img src='data:image/png;base64,{player_logo_base64}' width='50' style='vertical-align:middle; margin-right:-15px;'> <b>{player_name}</b>"
    #     except FileNotFoundError:
    #         st.error(f"Logo not found for player {player_name}")
    #         overview_data.loc[i, 'Name'] = f"<b>{player_name}</b>"

    # Table creation with row highlighting
    table_html = """
    <style>
    .styled-table {{
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
    }}
    .styled-table thead tr {{
        background-color: rgba(14, 17, 23, 0.70);
        color: #ffffff;
        text-align: left;
    }}
    .styled-table th,
    .styled-table td {{
        padding: 12px 15px;
        text-align: center;
    }}
    .styled-table tbody tr {{
        background-color: rgba(14, 17, 23, 0.35);
        border-bottom: 1px solid rgba(97, 101, 114, 0.9);
    }}
    .styled-table tbody tr.selected-player {{
        background-color: {highlight_color};
    }}
    .styled-table tbody tr:last-of-type {{
        border-bottom: 2px solid rgba(97, 101, 114, 0.9);
    }}
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
        row_class = "selected-player" if row['Name'].split('>')[-1].strip('</b>') == selected_player else ""
        table_html += f"<tr class='{row_class}'><td>{row['Rank']}</td><td>{row['+/-']}</td><td>{row['Name']}</td><td>{row['Matchday Points']}</td><td>{row['MD Winner']}</td><td>{row['MD Wins']}</td><td>{row['Total Points']}</td></tr>"

    table_html += "</tbody></table>"

    # Extract the highlight color for the selected player
    highlight_color = color_palette.get(selected_player, "rgba(14, 17, 23, 0.35)")

    # Display the Group Table with the highlight color applied
    st.markdown(table_html.format(highlight_color=highlight_color), unsafe_allow_html=True)

    # Histogram (Second)
    display_matchday_histogram(matchday, rankings_df, selected_players)

    # Density Plot (Third)
    display_season_density_plot(matchday, rankings_df, selected_players)

    # Bump Chart (Fourth)
    st.subheader("Bump Chart")
    display_bump_chart_group(rankings_df, matchday, selected_players)

    # Bar Chart (Fifth)
    st.subheader("Bar Chart")
    display_group_table_with_highlight(matchday, rankings_df, selected_player)

    # Add a Play Animation button for Bar Chart animation with unique key
    if st.button("Play Bar Chart Animation", key="bar_chart_animation"):
        fig_go = create_group_table_animation(rankings_df, selected_player=selected_player)
        st.plotly_chart(fig_go, use_container_width=True)

    # Donut Chart (Sixth)
    display_donut_chart(matchdays_df, selected_players, matchday)