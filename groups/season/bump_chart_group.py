import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
from io import BytesIO
import base64

# Define the color palette
color_palette = {
    "Andreas": "rgba(102, 194, 165, 0.85)",
    "Gerd": "rgba(252, 141, 98, 0.85)",
    "Geri": "rgba(141, 160, 203, 0.85)",
    "Hermann": "rgba(231, 138, 195, 0.85)",
    "Johnny": "rgba(166, 216, 84, 0.85)",
    "Moddy": "rgba(255, 217, 47, 0.85)",
    "Samson": "rgba(229, 196, 148, 0.85)",
    "Gray": "rgba(179, 179, 179, 0.50)"
}

# Utility function to convert an image to base64 for Plotly
def image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str

# Resize the image while maintaining the aspect ratio
def resize_image_uniform(image, target_size):
    original_width, original_height = image.size
    scaling_factor = target_size / min(original_width, original_height)
    new_width = int(original_width * scaling_factor)
    new_height = int(original_height * scaling_factor)
    return image.resize((new_width, new_height), Image.LANCZOS)

# Function to animate the bump chart with player faces
def animate_bump_chart_group(rankings_df, matchday, selected_players):
    fig = go.Figure()

    df_bump = rankings_df.pivot(index='Name', columns='Spieltag', values='Rang')

    # First, plot non-selected players' lines
    for player in df_bump.index:
        if selected_players == 'All' or player not in selected_players:
            line_color = color_palette["Gray"]
            player_data = rankings_df[(rankings_df['Name'] == player) & (rankings_df['Spieltag'] <= matchday)]

            fig.add_trace(go.Scatter(
                x=player_data['Spieltag'],
                y=player_data['Rang'],
                mode='lines+markers',
                marker=dict(size=5, color=line_color),
                line=dict(width=1.5, color=line_color),
                name=player
            ))

    # Plot selected players' lines
    for player in selected_players:
        if player in df_bump.index:
            line_color = color_palette.get(player, color_palette["Gray"])
            fig.add_trace(go.Scatter(
                x=df_bump.columns[df_bump.columns <= matchday],
                y=df_bump.loc[player][df_bump.columns <= matchday],
                mode='lines+markers',
                marker=dict(size=8, color=line_color),
                line=dict(width=4, color=line_color),
                name=player
            ))

    # Add initial player logos
    layout_images_initial = []
    for player in df_bump.index:
        player_data = rankings_df[(rankings_df['Name'] == player) & (rankings_df['Spieltag'] <= matchday)]
        if not player_data['Rang'][player_data['Spieltag'] == matchday].empty:
            end_x = matchday
            end_y = player_data['Rang'][player_data['Spieltag'] == matchday].values[0]
            player_logo_path = f"data/logos/groups/{player}.png"

            try:
                player_logo = Image.open(player_logo_path)
                resized_logo = resize_image_uniform(player_logo, 100)
                logo_base64 = image_to_base64(resized_logo)

                layout_images_initial.append(
                    dict(
                        source=f'data:image/png;base64,{logo_base64}',
                        xref="x", yref="y",
                        x=end_x - 0.5,
                        y=end_y,
                        sizex=3, sizey=3,
                        xanchor="left",
                        yanchor="middle",
                        layer="above"
                    )
                )
            except FileNotFoundError:
                st.error(f"Logo not found for player {player}")

    # Add initial images to the layout
    fig.update_layout(images=layout_images_initial)

    # Create frames for animation
    frames = []
    for md in range(1, matchday + 1):
        frame_data = []
        layout_images_frame = []

        for player in df_bump.index:
            player_data = rankings_df[(rankings_df['Name'] == player) & (rankings_df['Spieltag'] <= md)]
            if player not in selected_players:
                frame_data.append(go.Scatter(
                    x=player_data['Spieltag'],
                    y=player_data['Rang'],
                    mode='lines+markers',
                    marker=dict(size=5, color=color_palette["Gray"]),
                    line=dict(width=1.5, color=color_palette["Gray"]),
                    name=player
                ))

            # Add player logo regardless of selection
            if not player_data['Rang'][player_data['Spieltag'] == md].empty:
                end_x = md
                end_y = player_data['Rang'][player_data['Spieltag'] == md].values[0]
                player_logo_path = f"data/logos/groups/{player}.png"

                try:
                    player_logo = Image.open(player_logo_path)
                    resized_logo = resize_image_uniform(player_logo, 100)
                    logo_base64 = image_to_base64(resized_logo)

                    layout_images_frame.append(
                        dict(
                            source=f'data:image/png;base64,{logo_base64}',
                            xref="x", yref="y",
                            x=end_x - 0.5,
                            y=end_y,
                            sizex=3, sizey=3,
                            xanchor="left",
                            yanchor="middle",
                            layer="above"
                        )
                    )
                except FileNotFoundError:
                    continue

        for player in selected_players:
            if player in df_bump.index:
                player_data = rankings_df[(rankings_df['Name'] == player) & (rankings_df['Spieltag'] <= md)]
                frame_data.append(go.Scatter(
                    x=player_data['Spieltag'],
                    y=player_data['Rang'],
                    mode='lines+markers',
                    marker=dict(size=8, color=color_palette.get(player, color_palette["Gray"])),
                    line=dict(width=4, color=color_palette.get(player, color_palette["Gray"])),
                    name=player
                ))

        frames.append(go.Frame(data=frame_data, layout=dict(images=layout_images_frame), name=str(md)))

    fig.frames = frames

    # Add controls for playing and pausing animation
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                direction="left",
                x=0.1, y=-0.2,
                buttons=[dict(label="Play",
                              method="animate",
                              args=[None, {"frame": {"duration": 500, "redraw": True},
                                           "fromcurrent": True, "transition": {"duration": 500}}]),
                         dict(label="Pause",
                              method="animate",
                              args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])])
        ],
        sliders=[dict(
            steps=[dict(method="animate",
                        args=[[str(md)], {"mode": "immediate",
                                          "frame": {"duration": 500, "redraw": True},
                                          "transition": {"duration": 500}}],
                        label=f"{md}") for md in range(1, matchday + 1)],
            active=0,
            transition={"duration": 0},
            x=0.3, y=-0.2,
            xanchor="left", len=0.6,
            currentvalue={"prefix": "Matchday ", "suffix": ""}
        )]
    )

    # Layout and title updates
    fig.update_layout(
        title='Group Bump Chart Animation',
        xaxis=dict(
            title='Matchday',
            tickvals=list(range(1, 35)),
            ticktext=[str(i) for i in range(1, 35)],
            dtick=1,
            range=[0.5, 35.9],
            showgrid=True,
        ),
        yaxis=dict(
            title='Rank',
            autorange='reversed',
            tickvals=list(range(1, 8)),
            range=[0.5, 7.5],
            showgrid=True
        ),
        plot_bgcolor='rgba(14, 17, 23, 0.50)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,  
        width=800,  
        showlegend=False,
    )

    # Mid-season dotted line
    fig.add_vline(x=17.5, line=dict(color='rgba(255, 255, 255, 0.5)', dash='dot', width=1.5))

    st.plotly_chart(fig, use_container_width=True)

# Static Bump Chart
def display_bump_chart_group(rankings_df, matchday, selected_players):
    st.header("Bump Chart")
    df_bump = rankings_df.pivot(index='Name', columns='Spieltag', values='Rang')

    # Display static bump chart
    fig = go.Figure()

    for player in df_bump.index:
        line_color = color_palette["Gray"] if selected_players != 'All' and player not in selected_players else color_palette.get(player, "Gray")

        fig.add_trace(go.Scatter(
            x=df_bump.columns[df_bump.columns <= matchday],
            y=df_bump.loc[player][df_bump.columns <= matchday],
            mode='lines+markers',
            marker=dict(size=5 if player not in selected_players else 8, color=line_color),
            line=dict(width=1.5 if player not in selected_players else 4, color=line_color),
            name=player
        ))

        # Add player images at the end of their lines
        end_x = df_bump.columns[df_bump.columns <= matchday][-1]
        end_y = df_bump.loc[player][end_x]
        player_logo_path = f"data/logos/groups/{player}.png"
        try:
            player_logo = Image.open(player_logo_path)
            resized_logo = resize_image_uniform(player_logo, 100)
            logo_base64 = image_to_base64(resized_logo)

            fig.add_layout_image(
                dict(
                    source=f'data:image/png;base64,{logo_base64}',
                    xref="x", yref="y",
                    x=end_x - 0.5,
                    y=end_y,
                    sizex=3, sizey=3,
                    xanchor="left",
                    yanchor="middle",
                    layer="above"
                )
            )
        except FileNotFoundError:
            st.error(f"Logo not found for player {player}")

    fig.update_layout(
        title=f'Player Bump Chart - Matchday {matchday}',
        xaxis_title='Matchday',
        yaxis_title='Rank',
        yaxis=dict(autorange='reversed', tickvals=list(range(1, 8))),
        xaxis=dict(tickvals=list(range(1, 35)), dtick=1),
        plot_bgcolor='rgba(14, 17, 23, 0.50)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500, 
        width=800,   
        showlegend=False,
    )

    fig.add_vline(x=17.5, line=dict(color='rgba(255, 255, 255, 0.5)', dash='dot', width=1.5))

    st.plotly_chart(fig, use_container_width=True)

    # Single button for bump chart animation
    if st.button("Play Animation"):
        animate_bump_chart_group(rankings_df, matchday, selected_players)