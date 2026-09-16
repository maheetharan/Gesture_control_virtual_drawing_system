# ===============================
# AI DRAW PRO - ZERO LAG FULL PRO
# ===============================

import cv2
import numpy as np
import time

from ui import draw_ui, palette, button_coords
from camera import Camera
from hand_tracking import HandTracker
from gestures import fingers_up, is_fist, is_two_fingers, is_thumb_up, is_ok_gesture
from shapes import draw_shape
import config as cfg

# ================= INIT =================
cam = Camera(0)
tracker = HandTracker()

canvas = None
shape_start = None

undo_stack = []
redo_stack = []

frame_count = 0
PROCESS_FRAME_SKIP = 2

# SMOOTHING
smooth_x, smooth_y = 0, 0
alpha = 0.7

# DRAW
draw_points = []
MAX_POINTS = 10

# PATTERN
brush_patterns = ["solid", "dotted", "dashed", "hatched"]
current_pattern = "solid"

# LAYERS
layers = [None, None, None]
layer_visibility = [True, True, True]
current_layer = 0

for i in range(len(layers)):
    layers[i] = np.zeros((480, 640, 3), dtype=np.uint8)

# GESTURE COUNTERS
fist_counter = 0
save_counter = 0

# UI CACHE
ui_overlay = None
last_tool = None

# BUTTON DEBOUNCE
button_pressed = False

# ================= FUNCTIONS =================
def merge_layers():
    merged = layers[0].copy()
    for i in range(1, len(layers)):
        if layer_visibility[i]:
            cv2.add(merged, layers[i], merged)
    return merged

def smooth_point(x, y):
    global smooth_x, smooth_y
    smooth_x = int(alpha * smooth_x + (1 - alpha) * x)
    smooth_y = int(alpha * smooth_y + (1 - alpha) * y)
    return smooth_x, smooth_y

def draw_continuous_pattern(canvas, points, color, size, pattern):
    if len(points) < 2:
        return
    if pattern == "solid":
        for i in range(1, len(points)):
            cv2.line(canvas, points[i-1], points[i], color, size)
    elif pattern == "dotted":
        for i in range(0, len(points), 5):
            cv2.circle(canvas, points[i], size//2, color, -1)
    elif pattern == "dashed":
        for i in range(1, len(points)):
            if i % 6 < 3:
                cv2.line(canvas, points[i-1], points[i], color, size)
    elif pattern == "hatched":
        for i in range(0, len(points), 3):
            x, y = points[i]
            cv2.line(canvas, (x-5,y-5),(x+5,y+5), color, 1)
            cv2.line(canvas, (x+5,y-5),(x-5,y+5), color, 1)

# ================= MAIN LOOP =================
while True:
    ret, frame = cam.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    if canvas is None:
        canvas = np.zeros_like(frame)
        for i in range(len(layers)):
            layers[i] = np.zeros_like(frame)

    frame_count += 1

    # ================= HAND TRACKING =================
    if frame_count % PROCESS_FRAME_SKIP == 0:
        tracker.process(frame)

    display = frame.copy()

    if tracker.results and tracker.results.multi_hand_landmarks:
        for hand in tracker.results.multi_hand_landmarks:
            lm = hand.landmark

            raw_x, raw_y = int(lm[8].x * w), int(lm[8].y * h)
            ix, iy = smooth_point(raw_x, raw_y)

            thumb = (int(lm[4].x * w), int(lm[4].y * h))
            fingers = fingers_up(lm)
            index_only = fingers[1] and not any(fingers[2:])

            cv2.circle(display, (ix, iy), 6, cfg.color, -1)

            # ================= UI CLICK =================
            if index_only:
                pressed = False
                for btn_name, (x1,y1,x2,y2) in button_coords.items():
                    if x1 < ix < x2 and y1 < iy < y2:
                        cfg.tool = btn_name if btn_name in ["brush","eraser","line","rect","circle"] else cfg.tool
                        if btn_name.startswith("color"):
                            idx = int(btn_name[-1]) - 1  # last character is the number
                            cfg.color = palette[idx]
                            cfg.tool = "brush"
                        pressed = True
                        break
                if pressed and not button_pressed:
                    draw_points.clear()
                    button_pressed = True
                elif not pressed:
                    button_pressed = False

            # ================= GESTURES =================
            if is_fist(fingers):
                fist_counter += 1
                if fist_counter > 10:
                    layers[current_layer][:] = 0
                    undo_stack.clear()
                    redo_stack.clear()
                    fist_counter = 0
            else:
                fist_counter = 0

            if is_two_fingers(fingers):
                save_counter += 1
                if save_counter > 10:
                    filename = f"drawing_{int(time.time())}.png"
                    cv2.imwrite(filename, merge_layers())
                    print("Saved", filename)
                    save_counter = 0
            else:
                save_counter = 0

            if is_thumb_up(fingers) and undo_stack:
                redo_stack.append(layers[current_layer].copy())
                layers[current_layer] = undo_stack.pop()

            if is_ok_gesture(lm) and redo_stack:
                undo_stack.append(layers[current_layer].copy())
                layers[current_layer] = redo_stack.pop()

            # ================= DRAW =================
            if cfg.tool == "brush" and index_only:
                draw_points.append((ix, iy))
                if len(draw_points) > MAX_POINTS:
                    draw_points.pop(0)
                draw_continuous_pattern(layers[current_layer], draw_points, cfg.color, cfg.brush_size, current_pattern)
            else:
                draw_points.clear()

            # ERASER
            if cfg.tool == "eraser" and index_only:
                cv2.circle(layers[current_layer], (ix, iy), cfg.eraser_size, (0,0,0), -1)

    else:
        draw_points.clear()
        shape_start = None

    # ================= MERGE & DISPLAY =================
    merged = merge_layers()
    display = cv2.addWeighted(display, 0.7, merged, 1, 0)

    # Draw UI once
    if ui_overlay is None or cfg.tool != last_tool:
        ui_overlay = np.zeros_like(display)
        draw_ui(ui_overlay, cfg.tool)
        last_tool = cfg.tool

    display = cv2.add(display, ui_overlay)

    # Show pattern
    cv2.putText(display, f"Pattern: {current_pattern}", (10,120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    cv2.imshow("AI Draw PRO FULL PRO", display)

    key = cv2.waitKey(1)
    if key == 27:
        break
    elif key == ord('p'):
        idx = brush_patterns.index(current_pattern)
        current_pattern = brush_patterns[(idx+1)%len(brush_patterns)]

cam.release()
tracker.close()
cv2.destroyAllWindows()