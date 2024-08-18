from PIL import Image
from io import BytesIO
import base64

# Utility functions for match_preview.py
def resize_image(image, target_area):
    aspect_ratio = image.width / image.height
    new_width = int((target_area * aspect_ratio) ** 0.5)
    new_height = int((target_area / aspect_ratio) ** 0.5)
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

# Utility function to resize image to fit within a bounding box
def resize_image_to_bounding_box(image, target_width, target_height):
    aspect_ratio = image.width / image.height
    if aspect_ratio > 1:
        # Image is wider than it is tall
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:
        # Image is taller than it is wide
        new_height = target_height
        new_width = int(target_height * aspect_ratio)
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
# Utility functions for form_guide_last_5.py
def resize_logo(image, max_width=None, max_height=None):
    aspect_ratio = image.width / image.height
    
    if max_width is not None and max_height is None:
        new_width = min(image.width, max_width)
        new_height = int(new_width / aspect_ratio)
    elif max_height is not None and max_width is None:
        new_height = min(image.height, max_height)
        new_width = int(new_height * aspect_ratio)
    else:
        new_width = min(image.width, max_width)
        new_height = min(image.height, max_height)

    return image.resize((new_width, new_height), Image.LANCZOS)

def load_image(image_path):
    return Image.open(image_path)

# Utility function to convert image to base64 for Plotly
def image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# Utility function to get team colors
def get_team_colors(team_tag, color_codes_df):
    colors = color_codes_df[color_codes_df['Tag'] == team_tag]
    if not colors.empty:
        primary_color = colors.iloc[0]['Primary']
        secondary_color = colors.iloc[0]['Secondary']
        return primary_color, secondary_color
    return "#000000", "#FFFFFF"  # Default to black and white if colors not found
