import streamlit as st
from PIL import Image

# Set page configuration
st.set_page_config(page_title="Home", page_icon="⚽")

# Load and crop the image using Pillow
image = Image.open("data/logos/moneyball/moneyball.png")
cropped_image = image.crop(image.getbbox())  # Crop out unnecessary space

# CSS to center the image and text
st.markdown(
    """
    <style>
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: -150px; /* Adjust this value to move the logo higher */
    }
    .centered-text {
        display: flex;
        justify-content: center;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Start the centered content
st.markdown('<div class="centered">', unsafe_allow_html=True)

# Display the cropped image with a larger size
st.image(cropped_image, use_column_width=False, width=600)

# End the centered content
st.markdown('</div>', unsafe_allow_html=True)

