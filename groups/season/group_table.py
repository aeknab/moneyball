import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
from io import BytesIO
import base64

# Define the new ColorBrewer Set2 color palette for players with 85% transparency
color_palette = {
    "Andreas": "rgba(102, 194, 165, 0.85)",  # light green
    "Gerd": "rgba(252, 141, 98, 0.85)",      # light orange
    "Geri": "rgba(141, 160, 203, 0.85)",     # light blue
    "Hermann": "rgba(231, 138, 195, 0.85)",  # light pink
    "Johnny": "rgba(166, 216, 84, 0.85)",    # light lime green
    "Moddy": "rgba(255, 217, 47, 0.85)",     # light yellow
    "Samson": "rgba(229, 196, 148, 0.85)"    # light brown
}

# Utility function to convert an image to base64 for Plotly
def image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str

def display_group_table(matchday, rankings_df, selected_players):
    st.subheader("Group Table")

    # Filter rankings data up to and including the selected matchday
    filtered_rankings_df = rankings_df[(rankings_df['Spieltag'] <= matchday) & (rankings_df['Name'].isin(selected_players))]

    # Calculate the total points for each player up to and including the selected matchday
    player_points = filtered_rankings_df.groupby('Name')['Punkte'].sum().reindex(selected_players)

    # Sort the players by their total points
    player_points = player_points.sort_values(ascending=False)

    # Create a Plotly figure
    fig = go.Figure()

    # Add a bar for each player with their specific color
    for player in player_points.index:
        fig.add_trace(go.Bar(
            x=[player_points[player]],
            y=[player],
            orientation='h',
            name=player,
            marker=dict(color=color_palette.get(player, 'rgba(102, 194, 165, 0.85)'))  # Use player-specific color
        ))

        # Add player images at the end of the bars
        player_logo_path = f"data/logos/groups/{player}.png"  # Assume player logos are stored in this path
        player_logo = Image.open(player_logo_path)
        player_logo_resized = player_logo.resize((40, 40))  # Resize the logo
        logo_base64 = image_to_base64(player_logo_resized)

        # Position the logo to the right of the bar
        fig.add_layout_image(
            dict(
                source=f'data:image/png;base64,{logo_base64}',
                xref="x", yref="y",
                x=player_points[player] + 1,  # Position slightly to the right of the bar
                y=player,
                sizex=40 / fig.layout.xaxis.range[1],  # Adjust size to match bar height
                sizey=0.5,
                xanchor="left",
                yanchor="middle",
                layer="above"
            )
        )

        # Add player face logos next to their names
        fig.add_layout_image(
            dict(
                source=f'data:image/png;base64,{logo_base64}',
                xref="paper", yref="y",
                x=0.02,  # Position slightly to the left of the player's name
                y=player,
                sizex=0.04,  # Adjust size to match the name height
                sizey=0.5,
                xanchor="center",
                yanchor="middle",
                layer="above"
            )
        )

    # Update layout for the figure
    fig.update_layout(
        title_text=f'Group League Table - Matchday {matchday}',
        xaxis_title='Points',
        yaxis_title='Players',
        yaxis=dict(autorange='reversed'),  # Invert y-axis to have the top player at the top
        template='plotly_white',  # Optional: Use the 'plotly_white' theme for a clean look
        height=400,  # Adjust height if needed
        margin=dict(l=100, r=20, t=50, b=50)  # Adjust margins if needed
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Function to create an animated group table
def create_group_table_animation(rankings_df, selected_players):
    st.subheader("Animated Group Table")

    # Filter rankings data to include only the selected players
    filtered_rankings_df = rankings_df[rankings_df['Name'].isin(selected_players)]

    # Calculate the total points for each player across matchdays
    player_points_per_day = filtered_rankings_df.groupby(['Spieltag', 'Name'])['Punkte'].sum().reset_index()
    player_points_per_day = player_points_per_day.pivot(index='Spieltag', columns='Name', values='Punkte').fillna(0)
    player_points_per_day = player_points_per_day.cumsum().reset_index()

    # Melt the DataFrame for use in Plotly Express
    player_points_long = pd.melt(player_points_per_day, id_vars=['Spieltag'], var_name='Player', value_name='Points')

    # Create the animated bar chart
    fig = px.bar(player_points_long,
                 x='Points',
                 y='Player',
                 color='Player',
                 orientation='h',
                 animation_frame='Spieltag',
                 animation_group='Player',
                 range_x=[0, player_points_long['Points'].max() + 10],  # Adjust range as needed
                 color_discrete_map={player: color for player, color in color_palette.items() if player in selected_players})

    # Customize the layout
    fig.update_layout(
        yaxis=dict(autorange="reversed", title='Players'),
        xaxis=dict(title='Points'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=600,
        width=800
    )

    # Overlaying logos using Plotly graph_objects
    frames = []
    for spieltag in player_points_long['Spieltag'].unique():
        df_day = player_points_long[player_points_long['Spieltag'] == spieltag]
        layout_images_frame = []

        for _, row in df_day.iterrows():
            player_logo_path = f"data/logos/groups/{row['Player']}.png"
            player_logo = Image.open(player_logo_path)
            player_logo_resized = player_logo.resize((40, 40))  # Resize the logo
            logo_base64 = image_to_base64(player_logo_resized)

            layout_images_frame.append(
                dict(
                    source=f'data:image/png;base64,{logo_base64}',
                    xref="x",
                    yref="y",
                    x=row['Points'] + 2,  # Position slightly to the right of the bar
                    y=row['Player'],
                    sizex=5,  # Adjust size to match bar height
                    sizey=0.7,
                    xanchor="left",
                    yanchor="middle",
                    layer="above"
                )
            )

        # Combine the express data with graph_objects for each frame
        frames.append(go.Frame(data=fig.data, layout=dict(images=layout_images_frame), name=str(spieltag)))

    # Update the figure with frames
    fig_go = go.Figure(fig)
    fig_go.frames = frames

    # Add animation controls
    fig_go.update_layout(updatemenus=[dict(type="buttons",
                                           buttons=[dict(label="Play",
                                                         method="animate",
                                                         args=[None, {"frame": {"duration": 500, "redraw": True},
                                                                      "fromcurrent": True,
                                                                      "mode": "immediate"}]),
                                                    dict(label="Pause",
                                                         method="animate",
                                                         args=[[None], {"frame": {"duration": 0, "redraw": False},
                                                                        "mode": "immediate"}])])])

    st.plotly_chart(fig_go, use_container_width=True)

# Example usage in a Streamlit app
def main():
    # Assume you have a DataFrame `rankings_df` with columns 'Spieltag', 'Name', and 'Punkte'
    rankings_df = pd.read_csv('data/rankings.csv')  # Replace with the correct path
    selected_players = ["Andreas", "Gerd", "Geri", "Hermann", "Johnny", "Moddy", "Samson"]

    # Display the group table
    display_group_table(matchday=10, rankings_df=rankings_df, selected_players=selected_players)

    # Create and display the animated group table
    create_group_table_animation(rankings_df, selected_players)

if __name__ == "__main__":
    main()