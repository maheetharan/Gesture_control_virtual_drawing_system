# ===============================
# UI MODULE FOR AI DRAW PRO
# ===============================

import cv2
import numpy as np
from config import color

# ================= COLORS =================
palette = [
    (0, 0, 255),      # Red
    (0, 255, 0),      # Green
    (255, 0, 0),      # Blue
    (0, 255, 255),    # Yellow
    (255, 0, 255),    # Magenta
    (255, 255, 0),    # Cyan
    (255, 255, 255),  # White
    (0, 0, 0),        # Black
]

# ================= BUTTON COORDINATES =================
button_coords = {
    "color_1": (490, 0, 530, 70),
    "color_2": (540, 0, 580, 70),
    "color_3": (590, 0, 630, 70),
    "color_4": (640, 0, 680, 70),
    "color_5": (690, 0, 730, 70),
}

# ================= DRAW UI =================
def draw_ui(frame, current_tool):
    """
    Draw the top menu UI with buttons and colors
    """
    # Draw tool buttons
    for btn_name, (x1, y1, x2, y2) in button_coords.items():
        # Highlight selected tool
        if btn_name == current_tool:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), -1)
        else:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (50, 50, 50), -1)
        
        # Draw tool names
        if btn_name.startswith("color"):
            idx = int(btn_name[-1]) - 1
            cv2.rectangle(frame, (x1+5, y1+5), (x2-5, y2-5), palette[idx], -1)
        else:
            cv2.putText(frame, btn_name.capitalize(), (x1+5, y1+40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Draw separation line
    cv2.line(frame, (0, 70), (frame.shape[1], 70), (200, 200, 200), 2)