def fingers_up(lm):
    fingers = []
    fingers.append(lm[4].x < lm[3].x)

    tips = [8, 12, 16, 20]
    bases = [6, 10, 14, 18]

    for t, b in zip(tips, bases):
        fingers.append(lm[t].y < lm[b].y)

    return fingers

def is_fist(fingers):
    return not any(fingers)

def is_two_fingers(fingers):
    return fingers[1] and fingers[2] and not fingers[3] and not fingers[4]

def is_thumb_up(fingers):
    return fingers[0] and not any(fingers[1:])

def is_ok_gesture(lm):
    # thumb tip نزدیک index tip
    return abs(lm[4].x - lm[8].x) < 0.03 and abs(lm[4].y - lm[8].y) < 0.03