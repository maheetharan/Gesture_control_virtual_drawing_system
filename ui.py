import cv2

palette = [
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (0,255,255),
    (255,255,255)
]

def draw_ui(frame, tool, hover_x=None):
    cv2.rectangle(frame, (0,0), (1000,80), (40,40,40), -1)

    tools = ["brush","eraser","line","rect","circle","star","arrow"]

    x = 10
    for t in tools:
        color = (0,255,0) if tool == t else (200,200,200)

        # Hover effect
        if hover_x is not None and x < hover_x < x + 80:
            color = (0,255,255)

        cv2.putText(frame, t, (x,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    color, 2)
        x += 100

    # 🎨 Color palette
    cx = 720
    for c in palette:
        cv2.rectangle(frame, (cx,20), (cx+40,60), c, -1)
        cx += 50