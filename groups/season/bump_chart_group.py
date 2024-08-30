import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
from io import BytesIO
import base64

# Define the color palette
color_palette = {
    "Andreas": "rgba(102, 194, 165, 1.0)",  # Full transparency for selected player
    "Gerd": "rgba(252, 141, 98, 1.0)",      # Full transparency for selected player
    "Geri": "rgba(141, 160, 203, 1.0)",     # Full transparency for selected player
    "Hermann": "rgba(231, 138, 195, 1.0)",  # Full transparency for selected player
    "Johnny": "rgba(166, 216, 84, 1.0)",    # Full transparency for selected player
    "Moddy": "rgba(255, 217, 47, 1.0)",     # Full transparency for selected player
    "Samson": "rgba(229, 196, 148, 1.0)",   # Full transparency for selected player
    "Gray": "rgba(179, 179, 179, 0.75)"     # Reduced transparency for non-selected players
}

def image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str

def resize_image_uniform(image, target_size):
    original_width, original_height = image.size
    scaling_factor = target_size / min(original_width, original_height)
    new_width = int(original_width * scaling_factor)
    new_height = int(original_height * scaling_factor)
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    return resized_image

def display_group_bump_chart(matchday, rankings_df, selected_players):
    st.subheader("Bump Chart")

    # Filter rankings data up to and including the selected matchday
    filtered_rankings_df = rankings_df[rankings_df['Spieltag'] <= matchday]

    # Pivot the data to get ranks by matchday for each player
    df_bump = filtered_rankings_df.pivot(index='Name', columns='Spieltag', values='Rang')

    fig = go.Figure()

    # First, plot the non-selected players
    for player in df_bump.index:
        if selected_players == 'All' or player not in selected_players:
            line_color = color_palette["Gray"]  # Grey out other players
            line_width = 1  # Thinner line for non-selected players

            fig.add_trace(go.Scatter(
                x=df_bump.columns,
                y=df_bump.loc[player],
                mode='lines+markers',
                marker=dict(size=8, color=line_color),
                line=dict(width=line_width, color=line_color),
                name=player
            ))

            # Add player images at the end of their lines
            player_logo_path = f"data/logos/groups/{player}.png"
            try:
                player_logo = Image.open(player_logo_path)
                target_size = 100  # Keep target size
                player_logo_resized = resize_image_uniform(player_logo, target_size)
                logo_base64 = image_to_base64(player_logo_resized)

                end_x = df_bump.columns[-1]
                end_y = df_bump.loc[player].iloc[-1]

                fig.add_layout_image(
                    dict(
                        source=f'data:image/png;base64,{logo_base64}',
                        xref="x", yref="y",
                        x=end_x - 0.5,  # Slightly move the logos to the right, closer to the end of the line
                        y=end_y,
                        sizex=3,  # Maintain the logo size
                        sizey=3, 
                        xanchor="left",
                        yanchor="middle",
                        layer="above"
                    )
                )
            except FileNotFoundError:
                st.error(f"Logo not found for player {player}")
                continue

    # Then, plot the selected player(s) on top
    if selected_players != 'All':
        for player in selected_players:
            if player in df_bump.index:
                line_color = color_palette.get(player, color_palette[player])  # Full color for selected player
                line_width = 4  # Thicker line for selected player

                fig.add_trace(go.Scatter(
                    x=df_bump.columns,
                    y=df_bump.loc[player],
                    mode='lines+markers',
                    marker=dict(size=8, color=line_color),
                    line=dict(width=line_width, color=line_color),
                    name=player
                ))

                # Add player images at the end of their lines
                player_logo_path = f"data/logos/groups/{player}.png"
                try:
                    player_logo = Image.open(player_logo_path)
                    target_size = 100  # Keep target size
                    player_logo_resized = resize_image_uniform(player_logo, target_size)
                    logo_base64 = image_to_base64(player_logo_resized)

                    end_x = df_bump.columns[-1]
                    end_y = df_bump.loc[player].iloc[-1]

                    fig.add_layout_image(
                        dict(
                            source=f'data:image/png;base64,{logo_base64}',
                            xref="x", yref="y",
                            x=end_x - 0.5,  # Slightly move the logos to the right, closer to the end of the line
                            y=end_y,
                            sizex=3,  # Maintain the logo size
                            sizey=3, 
                            xanchor="left",
                            yanchor="middle",
                            layer="above"
                        )
                    )
                except FileNotFoundError:
                    st.error(f"Logo not found for player {player}")
                    continue

    # Update layout
    fig.update_layout(
        title_text=f'Player Bump Chart - Matchday {matchday}',
        xaxis_title='Matchday',
        yaxis_title='Rank',
        yaxis=dict(
            autorange='reversed',  # This keeps the rank order correct
            tickvals=list(range(1, 8)),  # Assuming 7 ranks for players
            range=[0.5, 7.5],  # Fine-tuning the range to compress space between lines
            showgrid=True
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 35)),
            ticktext=[str(i) for i in range(1, 35)],
            dtick=1,
            range=[0.5, 36],  # Slightly extend the x-axis to make space for logos without too much extra space
            showgrid=True,
        ),
        plot_bgcolor='rgba(14, 17, 23, 0.70)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,  # Reduced height to compress the space between lines
        width=800,
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)