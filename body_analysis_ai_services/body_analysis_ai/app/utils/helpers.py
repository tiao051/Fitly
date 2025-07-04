def get_xy(landmarks, idx, width, height):
    point = landmarks[idx]
    return int(point.x * width), int(point.y * height)

def distance(p1, p2):
    import numpy as np
    return np.linalg.norm(np.array(p1) - np.array(p2))
