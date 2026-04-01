import cv2
import numpy as np
import math
import time

from camera import Camera
from hand_tracking import HandTracker
from gestures import fingers_up, is_fist, is_two_fingers, is_thumb_up, is_ok_gesture
from shapes import draw_shape
from ui import draw_ui, palette
import config as cfg

cam = Camera(0)
tracker = HandTracker()

canvas = None
prev_x, prev_y = 0, 0
shape_start = None

undo_stack = []
redo_stack = []

frame_count = 0

# NEW FEATURES
color_hover_time = 0
selected_color_index = -1
fist_counter = 0
save_delay = 0

draw_points = []

while True:
    ret, frame = cam.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    if canvas is None:
        canvas = np.zeros_like(frame)

    frame_count += 1

    # ⚡ Better FPS
    if frame_count % 2 == 0:
        tracker.process(frame)

    if cfg.blur_enabled:
        k = cfg.blur_value
    if k % 2 == 0: 
        k += 1  # ensure odd
        blurred = cv2.GaussianBlur(frame, (k, k), 0)
        display = blurred.copy()
    elif key == ord('b'):
            cfg.blur_enabled = not cfg.blur_enabled

    elif key == ord('+'):
        cfg.blur_value += 4

    elif key == ord('-'):
        cfg.blur_value = max(5, cfg.blur_value - 4)
    else:
        display = frame.copy()

    # 🌈 Rainbow mode
    if cfg.rainbow_mode:
        cfg.hue = (cfg.hue + 2) % 180
        hsv = np.uint8([[[cfg.hue, 255, 255]]])
        cfg.color = tuple(cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0][0])

    if tracker.results and tracker.results.multi_hand_landmarks:
        for hand in tracker.results.multi_hand_landmarks:
            lm = hand.landmark

            ix, iy = int(lm[8].x * w), int(lm[8].y * h)
            thumb = (int(lm[4].x * w), int(lm[4].y * h))

            fingers = fingers_up(lm)
            index_only = fingers[1] and not any(fingers[2:])

            cv2.circle(display, (ix, iy), 8, cfg.color, -1)

            # ✊ CLEAR
            if is_fist(fingers):
                fist_counter += 1
                if fist_counter > 15:
                    canvas[:] = 0
                    undo_stack.clear()
                    redo_stack.clear()
            else:
                fist_counter = 0

            # 💾 SAVE
            if is_two_fingers(fingers):
                save_delay += 1
                if save_delay > 15:
                    filename = f"drawing_{int(time.time())}.png"
                    cv2.imwrite(filename, canvas)
                    print("Saved:", filename)
                    save_delay = 0
            else:
                save_delay = 0

            # 👍 UNDO
            if is_thumb_up(fingers) and undo_stack:
                redo_stack.append(canvas.copy())
                canvas = undo_stack.pop()

            # 👌 REDO
            if is_ok_gesture(lm) and redo_stack:
                undo_stack.append(canvas.copy())
                canvas = redo_stack.pop()

            # 🎛️ UI AREA
            if iy < 80 and index_only:
                tools = ["brush","eraser","line","rect","circle","star","arrow"]
                idx = ix // 100
                if idx < len(tools):
                    cfg.tool = tools[idx]

                # 🎨 Color selection (stable)
                cx = 720
                for i, c in enumerate(palette):
                    if cx < ix < cx + 40:
                        if selected_color_index == i:
                            color_hover_time += 1
                        else:
                            selected_color_index = i
                            color_hover_time = 0

                        if color_hover_time > 10:
                            cfg.color = c
                            cfg.rainbow_mode = False
                    cx += 50

                prev_x, prev_y = 0, 0
                shape_start = None
                continue

            pinch = np.hypot(ix - thumb[0], iy - thumb[1]) < 40

            # ✏️ BRUSH (SMOOTH)
            if cfg.tool == "brush" and index_only:
                draw_points.append((ix, iy))

                if len(draw_points) > 5:
                    smooth = draw_points[-10:]
                    for i in range(1, len(smooth)):
                        cv2.line(canvas, smooth[i-1], smooth[i], cfg.color, cfg.brush_size)

                prev_x, prev_y = ix, iy
            else:
                prev_x, prev_y = 0, 0
                draw_points.clear()

            # 🧽 ERASER
            if cfg.tool == "eraser" and index_only:
                undo_stack.append(canvas.copy())
                cv2.circle(canvas, (ix, iy), cfg.eraser_size, (0, 0, 0), -1)

            # 🔷 SHAPES
            if cfg.tool in ["line", "rect", "circle", "star", "arrow"]:
                if shape_start is None and index_only:
                    shape_start = (ix, iy)

                if shape_start:
                    temp = canvas.copy()
                    draw_shape(temp, cfg.tool, shape_start, (ix, iy), cfg.color, cfg.brush_size)
                    display = cv2.addWeighted(display, 1, temp, 1, 0)

                if pinch and shape_start:
                    undo_stack.append(canvas.copy())
                    draw_shape(canvas, cfg.tool, shape_start, (ix, iy), cfg.color, cfg.brush_size)
                    shape_start = None

    else:
        prev_x, prev_y = 0, 0
        shape_start = None
        draw_points.clear()

    display = cv2.addWeighted(display, 0.7, canvas, 1, 0)

    draw_ui(display, cfg.tool, ix if 'ix' in locals() else None)

    cv2.imshow("AI Draw PRO", display)

    key = cv2.waitKey(1)

    if key == 27:
        break
    elif key == ord('x'):
        canvas[:] = 0
    elif key == ord('r'):
        cfg.rainbow_mode = not cfg.rainbow_mode
    elif key == ord('z') and undo_stack:
        redo_stack.append(canvas.copy())
        canvas = undo_stack.pop()
    elif key == ord('y') and redo_stack:
        undo_stack.append(canvas.copy())
        canvas = redo_stack.pop()

cam.release()
tracker.close()
cv2.destroyAllWindows()