import math

def distance(lm1, lm2):
    return math.hypot(lm1.x - lm2.x, lm1.y - lm2.y)

def fingers_up(lm):
    fingers = []
    
    # Thumb: When open, the tip is further from the pinky base than the inner joint
    fingers.append(distance(lm[4], lm[17]) > distance(lm[3], lm[17]))

    # Other fingers: When extended, the tip is further from the wrist than the PIP joint
    # This distance-based approach works regardless of hand rotation (e.g. pointing down)
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]

    for t, p in zip(tips, pips):
        fingers.append(distance(lm[t], lm[0]) > distance(lm[p], lm[0]))

    return fingers

def is_fist(fingers):
    return not any(fingers)

def is_two_fingers(fingers):
    return fingers[1] and fingers[2] and not fingers[3] and not fingers[4]

def is_thumb_up(fingers):
    return fingers[0] and not any(fingers[1:])

def is_ok_gesture(lm):
    # thumb tip near index tip
    return distance(lm[4], lm[8]) < 0.05

def is_shaka(fingers):
    # Shaka: thumb up, pinky up, middle/index/ring down
    return fingers[0] and fingers[4] and not fingers[1] and not fingers[2] and not fingers[3]