import streamlit as st
from PIL import Image
from datetime import datetime

def display_profile_page():
    st.title("My Profile")
    
    # Profile Picture Upload
    st.header("Profile Picture")
    uploaded_image = st.file_uploader("Upload a profile picture", type=["png", "jpg", "jpeg"])
    
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.markdown(
            """
            <style>
            .circle-img {
                width: 150px;
                height: 150px;
                border-radius: 50%;
                object-fit: cover;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown(f'<img src="data:image/png;base64,{image_to_bytes(image)}" class="circle-img">', unsafe_allow_html=True)
    
    st.write("---")

    # Personal Info Section
    st.header("Personal Information")
    
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    
    # Birthday Input with 100 years range
    birthday = st.date_input(
        "Birthday",
        value=datetime(2000, 1, 1),  # Default date
        min_value=datetime(1924, 1, 1),  # Start from 100 years ago
        max_value=datetime.now()  # Up to today's date
    )
    
    pronouns = st.selectbox(
        "Pronouns",
        options=["He/Him", "She/Her", "They/Them", "Other"]
    )
    
    location = st.text_input("Location")  # Placeholder for a more advanced autocomplete solution
    
    st.write("---")

    # Favorite Club Selection
    st.header("Favorite Club")
    st.subheader("Select your favorite Bundesliga club")

    clubs = [
        {"name": "Bayern München", "tag": "FCB"},
        {"name": "Borussia Dortmund", "tag": "BVB"},
        # Add the rest of the 18 Bundesliga teams here...
    ]

    selected_club = None
    cols = st.columns(3)
    for i, club in enumerate(clubs):
        with cols[i % 3]:
            logo_path = f"data/logos/team_logos/{club['tag']}.svg.png"
            if st.markdown(
                f"""
                <div style="text-align:center;">
                    <button class="team-button" onclick="window.location.reload()">
                        <img src="{logo_path}" style="width:80px;height:80px;">
                        <div>{club['name']}</div>
                    </button>
                </div>
                """,
                unsafe_allow_html=True
            ):
                selected_club = club['name']

    if selected_club:
        st.write(f"Your favorite club is: {selected_club}")
    
    st.write("---")

    # Relationships
    st.header("Relationships")
    st.write("Describe your relationships with other users (e.g., family members).")

    relationship_with = st.text_input("Who is this person to you?")
    relation = st.selectbox("Relationship", options=["Family", "Friend", "Colleague", "Other"])

    if st.button("Add Relationship"):
        st.write(f"Added relationship: {relation} - {relationship_with}")
    
    st.write("---")

    # Profile Color Selection
    st.header("Profile Color")
    
    # Club colors (assuming these are predefined)
    club_colors = {
        "Bayern München": {"primary": "#DC052D", "secondary": "#0066B2"},
        "Borussia Dortmund": {"primary": "#FFCC00", "secondary": "#000000"},
        # Add the rest of the clubs...
    }

    if selected_club and selected_club in club_colors:
        primary_color = club_colors[selected_club]["primary"]
        secondary_color = club_colors[selected_club]["secondary"]
        st.write(f"Club Colors: Primary - {primary_color}, Secondary - {secondary_color}")

    color_choice = st.radio("Choose a color", options=["Primary Club Color", "Secondary Club Color", "Standard Color", "Custom Color"])

    if color_choice == "Primary Club Color":
        selected_color = primary_color
    elif color_choice == "Secondary Club Color":
        selected_color = secondary_color
    elif color_choice == "Standard Color":
        selected_color = st.selectbox("Choose a standard color", options=["Red", "Blue", "Yellow", "Green", "Orange", "Purple"])
    elif color_choice == "Custom Color":
        selected_color = st.color_picker("Pick a custom color")
    
    st.write(f"Selected Color: {selected_color}")

# Utility function to convert an image to bytes (needed for displaying the image)
def image_to_bytes(image):
    import base64
    from io import BytesIO
    
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str
