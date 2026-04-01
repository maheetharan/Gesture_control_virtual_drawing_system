import cv2
import numpy as np
import math

def draw_star(img, center, size, color, thickness):
    cx, cy = center
    pts = []

    for i in range(10):
        angle = i * 36 * math.pi / 180
        r = size if i % 2 == 0 else size // 2
        x = int(cx + r * math.cos(angle))
        y = int(cy + r * math.sin(angle))
        pts.append((x, y))

    pts = np.array(pts, np.int32)
    cv2.polylines(img, [pts], True, color, thickness)

def draw_shape(img, tool, p1, p2, color, size):
    if tool == "line":
        cv2.line(img, p1, p2, color, size)

    elif tool == "rect":
        cv2.rectangle(img, p1, p2, color, size)

    elif tool == "circle":
        r = int(np.hypot(p1[0] - p2[0], p1[1] - p2[1]))
        cv2.circle(img, p1, r, color, size)

    elif tool == "star":
        draw_star(img, p1,
                  int(np.hypot(p1[0] - p2[0], p1[1] - p2[1])),
                  color, size)

    elif tool == "arrow":
        cv2.arrowedLine(img, p1, p2, color, size, tipLength=0.3)

def smooth_line(points):
    if len(points) < 5:
        return points

    pts = np.array(points, dtype=np.int32)
    epsilon = 0.01 * cv2.arcLength(pts, False)
    approx = cv2.approxPolyDP(pts, epsilon, False)

    return approx.reshape(-1, 2)