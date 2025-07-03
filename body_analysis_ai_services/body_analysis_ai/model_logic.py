# model_logic.py
from PIL import Image
import random

def analyze_body(image: Image.Image, gender: str):
    body_shapes_male = ["V-Taper", "Rectangle", "Oval", "Inverted Triangle"]
    body_shapes_female = ["Hourglass", "Pear", "Rectangle", "Oval"]
    somatotypes = ["Ectomorph", "Mesomorph", "Endomorph"]

    body_shape = random.choice(body_shapes_male if gender == "male" else body_shapes_female)
    somato = random.choice(somatotypes)

    return {
        "Somatotype": somato,
        "BodyShape": body_shape,
        "Confidence": round(random.uniform(0.8, 0.95), 2)
    }
