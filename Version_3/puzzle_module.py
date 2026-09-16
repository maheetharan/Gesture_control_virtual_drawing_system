import cv2
import random
import numpy as np

class PuzzlePiece:
    def __init__(self, img_segment, correct_pos, current_pos, size):
        self.img = img_segment
        self.correct_pos = correct_pos # (x, y) on the target grid
        self.pos = list(current_pos)   # (x, y) current floating position
        self.size = size
        self.is_locked = False

    def update_pos(self, center_x, center_y):
        if not self.is_locked:
            self.pos = [center_x - self.size // 2, center_y - self.size // 2]

    def check_snap(self, threshold=40):
        dist = np.sqrt((self.pos[0] - self.correct_pos[0])**2 + (self.pos[1] - self.correct_pos[1])**2)
        if dist < threshold:
            self.pos = list(self.correct_pos)
            self.is_locked = True
            return True
        return False

def create_puzzle(image, grid_size=3, offset_x=800, offset_y=150):
    h, w, _ = image.shape
    p_h, p_w = h // grid_size, w // grid_size
    pieces = []
    
    for i in range(grid_size):
        for j in range(grid_size):
            # Crop piece
            y1, y2 = i * p_h, (i + 1) * p_h
            x1, x2 = j * p_w, (j + 1) * p_w
            segment = image[y1:y2, x1:x2]
            
            # Target position on the RIGHT side grid
            target_x = offset_x + (j * p_w)
            target_y = offset_y + (i * p_h)
            
            # Initial random position on the LEFT side
            start_x = random.randint(50, 400)
            start_y = random.randint(100, 500)
            
            pieces.append(PuzzlePiece(segment, (target_x, target_y), (start_x, start_y), p_w))
    
    random.shuffle(pieces)
    return pieces