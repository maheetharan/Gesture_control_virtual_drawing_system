# ===============================
# AI DRAW PRO - ZERO LAG FULL PRO
# ===============================

import cv2
import numpy as np
import time

from ui import draw_ui, palette, button_coords
from camera import Camera
from hand_tracking import HandTracker
from gestures import fingers_up, is_fist, is_two_fingers, is_thumb_up, is_ok_gesture, is_shaka
from shapes import draw_shape
import config as cfg

# ================= INIT =================
cam = Camera(0)
tracker = HandTracker()

canvas = None
shape_start = None

undo_stack = []
redo_stack = []
is_erasing = False

frame_count = 0
PROCESS_FRAME_SKIP = 1

# SMOOTHING
smooth_x, smooth_y = 0, 0
alpha = 0.2

# DRAW
draw_points = []
MAX_POINTS = 10

# PATTERN
brush_patterns = ["solid", "dotted", "dashed", "hatched"]
current_pattern = "solid"

# GESTURE COUNTERS
fist_counter = 0
save_counter = 0

# UI CACHE
ui_overlay = None
last_tool = None

# BUTTON DEBOUNCE
button_pressed = False

status_text = ""
status_timer = 0.0

# ================= FUNCTIONS =================
def smooth_point(x, y):
    global smooth_x, smooth_y
    if smooth_x == 0 and smooth_y == 0:
        smooth_x, smooth_y = x, y
    else:
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

    # Initialize canvas
    if canvas is None:
        canvas = np.zeros_like(frame)

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

            fingers = fingers_up(lm)
            index_only = fingers[1] and not any(fingers[2:])

            # Determine drawing color (Rainbow Mode vs Selected Color)
            if cfg.rainbow_mode:
                cfg.hue = (cfg.hue + 2) % 180
                hsv_color = np.uint8([[[cfg.hue, 255, 255]]])
                bgr_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)[0][0]
                current_color = (int(bgr_color[0]), int(bgr_color[1]), int(bgr_color[2]))
            else:
                current_color = cfg.color

            cv2.circle(display, (ix, iy), 6, current_color, -1)

            # ================= UI CLICK =================
            if index_only:
                pressed = False
                for btn_name, (x1, y1, x2, y2) in button_coords.items():
                    if x1 < ix < x2 and y1 < iy < y2:
                        pressed = True
                        if not button_pressed:
                            if btn_name in ["brush", "eraser", "line", "rect", "circle", "star", "arrow"]:
                                cfg.tool = btn_name
                            elif btn_name.startswith("color"):
                                idx = int(btn_name.split("_")[-1]) - 1
                                cfg.color = palette[idx]
                                cfg.tool = "brush"
                                cfg.rainbow_mode = False
                            elif btn_name == "pattern":
                                idx = brush_patterns.index(current_pattern)
                                current_pattern = brush_patterns[(idx+1)%len(brush_patterns)]
                                status_text = f"Pattern: {current_pattern.capitalize()}"
                                status_timer = time.time()
                            elif btn_name == "undo":
                                if undo_stack:
                                    redo_stack.append(canvas.copy())
                                    canvas = undo_stack.pop()
                            elif btn_name == "redo":
                                if redo_stack:
                                    undo_stack.append(canvas.copy())
                                    canvas = redo_stack.pop()
                            elif btn_name == "clear":
                                if len(undo_stack) >= 20:
                                    undo_stack.pop(0)
                                if np.any(canvas):
                                    undo_stack.append(canvas.copy())
                                    redo_stack.clear()
                                    canvas[:] = 0
                            elif btn_name == "save":
                                filename = f"drawing_{int(time.time())}.png"
                                cv2.imwrite(filename, canvas)
                                status_text = f"Saved: {filename}"
                                status_timer = time.time()
                                print("Saved", filename)
                            elif btn_name == "rainbow":
                                cfg.rainbow_mode = not cfg.rainbow_mode
                        break
                if pressed and not button_pressed:
                    draw_points.clear()
                    button_pressed = True
                elif not pressed:
                    button_pressed = False

            # ================= GESTURES =================
            if is_shaka(fingers):
                fist_counter += 1
                if fist_counter > 10:
                    if np.any(canvas):
                        undo_stack.append(canvas.copy())
                        redo_stack.clear()
                        canvas[:] = 0
                    fist_counter = 0
            else:
                fist_counter = 0

            if is_two_fingers(fingers):
                save_counter += 1
                if save_counter > 10:
                    filename = f"drawing_{int(time.time())}.png"
                    cv2.imwrite(filename, canvas)
                    print("Saved", filename)
                    status_text = f"Saved: {filename}"
                    status_timer = time.time()
                    save_counter = 0
            else:
                save_counter = 0

            if is_thumb_up(fingers) and undo_stack:
                redo_stack.append(canvas.copy())
                canvas = undo_stack.pop()

            if is_ok_gesture(lm) and redo_stack:
                undo_stack.append(canvas.copy())
                canvas = redo_stack.pop()

            # ================= DRAW =================
            if cfg.tool == "brush" and index_only:
                if not draw_points:
                    if len(undo_stack) >= 20:
                        undo_stack.pop(0)
                    undo_stack.append(canvas.copy())
                    redo_stack.clear()
                draw_points.append((ix, iy))
                if len(draw_points) > MAX_POINTS:
                    draw_points.pop(0)
                draw_continuous_pattern(canvas, draw_points, current_color, cfg.brush_size, current_pattern)
            else:
                draw_points.clear()

            # ERASER
            if cfg.tool == "eraser" and index_only:
                if not is_erasing:
                    if len(undo_stack) >= 20:
                        undo_stack.pop(0)
                    undo_stack.append(canvas.copy())
                    redo_stack.clear()
                    is_erasing = True
                cv2.circle(canvas, (ix, iy), cfg.eraser_size, (0,0,0), -1)
            else:
                is_erasing = False

            # SHAPES (line, rect, circle, star, arrow)
            if cfg.tool in ["line", "rect", "circle", "star", "arrow"]:
                if index_only:
                    if shape_start is None:
                        shape_start = (ix, iy)
                    draw_shape(display, cfg.tool, shape_start, (ix, iy), current_color, cfg.brush_size)
                else:
                    if shape_start is not None:
                        if len(undo_stack) >= 20:
                            undo_stack.pop(0)
                        undo_stack.append(canvas.copy())
                        redo_stack.clear()
                        draw_shape(canvas, cfg.tool, shape_start, (ix, iy), current_color, cfg.brush_size)
                        shape_start = None

    else:
        draw_points.clear()
        if shape_start is not None:
            if smooth_x != 0 or smooth_y != 0:
                if len(undo_stack) >= 20:
                    undo_stack.pop(0)
                undo_stack.append(canvas.copy())
                redo_stack.clear()
                if cfg.rainbow_mode:
                    cfg.hue = (cfg.hue + 2) % 180
                    hsv_color = np.uint8([[[cfg.hue, 255, 255]]])
                    bgr_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)[0][0]
                    current_color = (int(bgr_color[0]), int(bgr_color[1]), int(bgr_color[2]))
                else:
                    current_color = cfg.color
                draw_shape(canvas, cfg.tool, shape_start, (smooth_x, smooth_y), current_color, cfg.brush_size)
            shape_start = None
        smooth_x, smooth_y = 0, 0
        is_erasing = False

    # ================= MERGE & DISPLAY =================
    # Fast overlay using addWeighted
    display = cv2.addWeighted(display, 0.7, canvas, 1.0, 0)

    # Draw UI once
    if ui_overlay is None or cfg.tool != last_tool:
        ui_overlay = np.zeros_like(display)
        draw_ui(ui_overlay, cfg.tool)
        last_tool = cfg.tool

    # Redraw UI frame overlay
    display = cv2.add(display, ui_overlay)

    # Show pattern
    cv2.putText(display, f"Pattern: {current_pattern}", (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Show Status / Toast notifications
    if time.time() - status_timer < 3.0:
        cv2.putText(display, status_text, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow("AI Draw PRO FULL PRO", display)

    key = cv2.waitKey(1)
    if key == 27:
        break
    elif key == ord('p') or key == ord('P'):
        idx = brush_patterns.index(current_pattern)
        current_pattern = brush_patterns[(idx+1)%len(brush_patterns)]
        status_text = f"Pattern: {current_pattern.capitalize()}"
        status_timer = time.time()

cam.release()
tracker.close()
cv2.destroyAllWindows()