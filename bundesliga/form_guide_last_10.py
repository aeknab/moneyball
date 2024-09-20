import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import base64
from io import BytesIO
import pandas as pd

# Function to resize the image
def resize_image(image, max_width, max_height):
    width, height = image.size
    aspect_ratio = width / height

    if width > max_width or height > max_height:
        if aspect_ratio > 1:
            width = max_width
            height = int(max_width / aspect_ratio)
        else:
            height = max_height
            width = int(max_height * aspect_ratio)
    
    return image.resize((width, height), Image.LANCZOS)

# Function to get team colors
def get_team_colors(team_tag, color_codes_df):
    colors = color_codes_df[color_codes_df['Tag'] == team_tag]
    if not colors.empty:
        primary_color = colors.iloc[0]['Primary']
        secondary_color = colors.iloc[0]['Secondary']
        return primary_color, secondary_color
    return "#000000", "#FFFFFF"

# Function to get the last 10 meetings *before* the current match
def get_last_10_meetings(df, home_team_tag, away_team_tag, color_codes_df, current_matchday, current_season):
    df['Match Date'] = pd.to_datetime(df['Match Date'])

    # Filter the matches between the teams, but only from seasons earlier than the current one
    matches_between_teams = df[
        (((df['Home Tag'] == home_team_tag) & (df['Away Tag'] == away_team_tag)) | 
         ((df['Home Tag'] == away_team_tag) & (df['Away Tag'] == home_team_tag))) & 
        ((df['Season'] < current_season) | ((df['Season'] == current_season) & (df['Matchday'] < current_matchday)))
    ].sort_values(by='Match Date', ascending=False).head(10)

    # Now, calculate wins, ties, and losses based on these past meetings
    home_wins = matches_between_teams[
        ((matches_between_teams['Home Tag'] == home_team_tag) & (matches_between_teams['Home Goals'] > matches_between_teams['Away Goals'])) |
        ((matches_between_teams['Away Tag'] == home_team_tag) & (matches_between_teams['Away Goals'] > matches_between_teams['Home Goals']))
    ]
    
    ties = matches_between_teams[
        matches_between_teams['Home Goals'] == matches_between_teams['Away Goals']
    ]
    
    away_wins = matches_between_teams[
        ((matches_between_teams['Home Tag'] == away_team_tag) & (matches_between_teams['Home Goals'] > matches_between_teams['Away Goals'])) |
        ((matches_between_teams['Away Tag'] == away_team_tag) & (matches_between_teams['Away Goals'] > matches_between_teams['Home Goals']))
    ]

    home_primary, home_secondary = get_team_colors(home_team_tag, color_codes_df)
    away_primary, away_secondary = get_team_colors(away_team_tag, color_codes_df)
    
    away_color = away_primary
    
    return home_wins, ties, away_wins, home_primary, away_color

# Function to plot the last 10 meetings
def plot_last_10_meetings(df, home_team_tag, away_team_tag, color_codes_df, current_matchday, current_season):
    home_wins, ties, away_wins, home_color, away_color = get_last_10_meetings(
        df, home_team_tag, away_team_tag, color_codes_df, current_matchday, current_season
    )
    
    total_matches = len(home_wins) + len(ties) + len(away_wins)

    # Determine if the selected season is the current one (2023/24)
    is_current_season = current_season == '2023/24'
    
    # Insert this in your script right before the Last 10 Meetings section
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)  # Adjust the margin-top value as needed

    if total_matches > 0:
        st.subheader(f"Last {total_matches} Meeting{'s' if total_matches > 1 else ''} between {home_team_tag} and {away_team_tag}", anchor=False)

        x_values = []
        colors = []
        hover_texts = []
        image_positions = []

        for idx, match in home_wins.iterrows():
            if match['Home Tag'] == home_team_tag:
                hover_text = f"{match['Match Date'].strftime('%d.%m.%y')}<br>(H) {match['Home Goals']} - {match['Away Goals']}"
            else:
                hover_text = f"{match['Match Date'].strftime('%d.%m.%y')}<br>(A) {match['Away Goals']} - {match['Home Goals']}"
            x_values.append(1)
            colors.append(home_color)
            hover_texts.append(hover_text)
            image_positions.append(len(x_values) - 1)

        for idx, match in ties.iterrows():
            hover_text = f"{match['Match Date'].strftime('%d.%m.%y')}<br>(H-{match['Home Tag']}) {match['Home Goals']} - {match['Away Goals']}"
            x_values.append(1)
            colors.append("#BBBBBB")
            hover_texts.append(hover_text)
            image_positions.append(len(x_values) - 1)

        for idx, match in away_wins.iterrows():
            if match['Home Tag'] == away_team_tag:
                hover_text = f"{match['Match Date'].strftime('%d.%m.%y')}<br>(H) {match['Home Goals']} - {match['Away Goals']}"
            else:
                hover_text = f"{match['Match Date'].strftime('%d.%m.%y')}<br>(A) {match['Away Goals']} - {match['Home Goals']}"
            x_values.append(1)
            colors.append(away_color)
            hover_texts.append(hover_text)
            image_positions.append(len(x_values) - 1)

        fig = go.Figure(go.Bar(
            y=[''] * len(x_values),
            x=x_values,
            marker=dict(color=colors, line=dict(color='#696969', width=2)),  # Use border color
            orientation='h',
            hovertext=hover_texts,
            hoverinfo="text",
            width=0.6,  # Adjust the bar height for thickness
        ))

        fig.update_layout(
            barmode='stack',
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            plot_bgcolor='rgb(14, 17, 23)',
            paper_bgcolor='rgb(14, 17, 23)',
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),  # Reduced margin for better positioning
            height=250,  # Adjusted height for the bar
            width=1000,   # Ensure the bar is centered by matching width
        )

        # Load and resize team logos
        home_logo_path = f"data/logos/team_logos/{home_team_tag}.svg.png"
        away_logo_path = f"data/logos/team_logos/{away_team_tag}.svg.png"
        
        home_logo = Image.open(home_logo_path)
        away_logo = Image.open(away_logo_path)
        
        home_logo_resized = resize_image(home_logo, 60, 60)  # Adjusted logo size to fit within the bar
        away_logo_resized = resize_image(away_logo, 60, 60)

        def image_to_base64(image):
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return img_str
        
        home_logo_base64 = image_to_base64(home_logo_resized)
        away_logo_base64 = image_to_base64(away_logo_resized)

        # Add the home logo within the home wins section
        fig.add_layout_image(
            dict(
                source=f'data:image/png;base64,{home_logo_base64}',
                xref="x", yref="paper",
                x=image_positions[0] + 0.5, y=0.5,
                sizex=0.5, sizey=0.5,  # Adjust the size to fit within the section
                xanchor="center", yanchor="middle"
            )
        )

        # Add the away logo within the away wins section
        fig.add_layout_image(
            dict(
                source=f'data:image/png;base64,{away_logo_base64}',
                xref="x", yref="paper",
                x=image_positions[-1] + 0.5, y=0.5,
                sizex=0.5, sizey=0.5,  # Adjust the size to fit within the section
                xanchor="center", yanchor="middle"
            )
        )

        # Display the chart
        st.plotly_chart(fig, use_container_width=True)

        # Display the legend below the chart
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin: -50px 10px 0 -30px;">
                <div style="width: 10%;"></div>  <!-- Empty column to create space on the left -->
                <div style="display: flex; align-items: center; justify-content: flex-start; width: 23%;">
                    <div style="width: 15px; height: 15px; background-color:{home_color}; margin-right: 5px; border: 1px solid #696969;"></div>
                    <span>{len(home_wins)} Wins</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: center; width: 23%;">
                    <div style="width: 15px; height: 15px; background-color:#BBBBBB; margin-right: 5px; border: 1px solid #696969;"></div>
                    <span>{len(ties)} Ties</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: flex-end; width: 23%;">
                    <span>{len(away_wins)} Wins</span>
                    <div style="width: 15px; height: 15px; background-color:{away_color}; margin-left: 5px; border: 1px solid #696969;"></div>
                </div>
                <div style="width: 10%;"></div>  <!-- Empty column to create space on the right -->
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        # If there are no previous matches between the teams
        st.write(f"No previous meetings between {home_team_tag} and {away_team_tag}.")