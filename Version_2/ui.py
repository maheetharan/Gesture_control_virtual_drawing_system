# ===============================
# UI MODULE FOR AI DRAW PRO
# ===============================

import cv2
import numpy as np

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
    # Tools (60px width each)
    "brush": (0, 0, 60, 70),
    "eraser": (60, 0, 120, 70),
    "line": (120, 0, 180, 70),
    "rect": (180, 0, 240, 70),
    "circle": (240, 0, 300, 70),
    "star": (300, 0, 360, 70),
    "arrow": (360, 0, 420, 70),
    
    # Colors (30px width each)
    "color_1": (420, 0, 450, 70),
    "color_2": (450, 0, 480, 70),
    "color_3": (480, 0, 510, 70),
    "color_4": (510, 0, 540, 70),
    "color_5": (540, 0, 570, 70),
    "color_6": (570, 0, 600, 70),
    "color_7": (600, 0, 630, 70),
    "color_8": (630, 0, 660, 70),
    
    # Utilities (50px width each)
    "pattern": (660, 0, 710, 70),
    "undo": (710, 0, 760, 70),
    "redo": (760, 0, 810, 70),
    "clear": (810, 0, 860, 70),
    "save": (860, 0, 910, 70),
    "rainbow": (910, 0, 960, 70),
}

# ================= DRAW UI =================
def draw_ui(frame, current_tool):
    """
    Draw the top menu UI with buttons and colors
    """
    import config as cfg
    
    # Draw tool buttons
    for btn_name, (x1, y1, x2, y2) in button_coords.items():
        # Highlight selected tool or mode
        is_highlighted = False
        if btn_name == current_tool:
            is_highlighted = True
        elif btn_name == "rainbow" and getattr(cfg, "rainbow_mode", False):
            is_highlighted = True

        if is_highlighted:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), -1)
        else:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (50, 50, 50), -1)
        
        # Draw tool names / color boxes
        if btn_name.startswith("color"):
            idx = int(btn_name.split("_")[-1]) - 1
            cv2.rectangle(frame, (x1+5, y1+5), (x2-5, y2-5), palette[idx], -1)
        else:
            label = btn_name.capitalize()
            if btn_name == "pattern":
                label = "Pat"
            elif btn_name == "rainbow":
                label = "Rain"
            
            # Put text centered
            text_color = (0, 0, 0) if is_highlighted else (255, 255, 255)
            font_scale = 0.4
            thickness = 1
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
            text_x = x1 + (x2 - x1 - text_size[0]) // 2
            text_y = y1 + (y2 - y1 + text_size[1]) // 2
            
            cv2.putText(frame, label, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness, cv2.LINE_AA)

    # Draw separation line
    cv2.line(frame, (0, 70), (frame.shape[1], 70), (200, 200, 200), 2)