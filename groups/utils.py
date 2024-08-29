import base64
from io import BytesIO
from PIL import Image

def format_points(points):
    """Formats points with color based on the score."""
    if points == 0:
        return f"<span style='color:grey'>({points})</span>"
    elif points == 2:
        return f"<span style='color:yellow'>({points})</span>"
    elif points == 3:
        return f"<span style='color:orange'>({points})</span>"
    elif points == 4:
        return f"<span style='color:red'>({points})</span>"
    return f"({points})"

def calculate_points(pred_home, pred_away, actual_home, actual_away):
    """Calculates points based on prediction and actual results."""
    pred_diff = pred_home - pred_away
    actual_diff = actual_home - actual_away

    if pred_home == actual_home and pred_away == actual_away:
        return 4  # Exact score
    elif pred_diff == actual_diff:
        if pred_diff == 0:  # Both predicted and actual results are ties but with different scores
            return 2
        return 3  # Correct goal difference
    elif (pred_home > pred_away and actual_home > actual_away) or (pred_home < pred_away and actual_home < actual_away):
        return 2  # Correct outcome/tendency
    else:
        return 0  # Wrong prediction

def image_to_base64(image):
    """
    Convert a PIL image to a base64 encoded string.
    """
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def resize_image_to_bounding_box(image: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """
    Resize an image to fit within a bounding box of target_width and target_height while maintaining aspect ratio.
    :param image: A PIL Image object to resize.
    :param target_width: The width of the bounding box.
    :param target_height: The height of the bounding box.
    :return: A resized PIL Image object.
    """
    # Calculate the appropriate scale factor to fit the image within the bounding box
    width_ratio = target_width / image.width
    height_ratio = target_height / image.height
    scale_factor = min(width_ratio, height_ratio)

    # Calculate new dimensions
    new_width = int(image.width * scale_factor)
    new_height = int(image.height * scale_factor)

    # Resize the image
    resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)

    return resized_image