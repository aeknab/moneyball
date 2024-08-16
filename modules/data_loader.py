import pandas as pd
from PIL import Image

def load_data():
    return pd.read_csv('data/BuLi_All_Seasons.csv')

def load_colors():
    return pd.read_csv('data/Color_Codes.csv')

def load_image(image_path):
    return Image.open(image_path)
