# ================== CONFIG DEFAULTS ==================
tool = "brush"       # Current selected tool
color = (0, 0, 255)  # Default brush color (BGR)
brush_size = 5
eraser_size = 20

rainbow_mode = False
hue = 0
button_coords = {
    "brush": (0, 0, 70, 80),
    "eraser": (70, 0, 140, 80),
    "line": (140, 0, 210, 80),
    "rect": (210, 0, 280, 80),
    "circle": (280, 0, 350, 80),
    # Colors
    "color_red": (720, 0, 760, 40),
    "color_green": (770, 0, 810, 40),
    "color_blue": (820, 0, 860, 40),
    "color_yellow": (870, 0, 910, 40),
    # Star & Arrow (example positions)
    "star": (360, 0, 430, 80),
    "arrow": (440, 0, 510, 80)
}