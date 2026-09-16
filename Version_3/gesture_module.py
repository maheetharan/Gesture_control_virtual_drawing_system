import cv2
import mediapipe as mp
import math

class GestureController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=1,
                                        model_complexity=1,
                                        min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils

    def get_landmarks(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize image for faster mediapipe processing without losing accuracy
        h, w = img.shape[:2]
        small_rgb = cv2.resize(img_rgb, (640, int(640 * h / w)))
        
        results = self.hands.process(small_rgb)
        lm_list = []
        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                for id, lm in enumerate(hand_lms.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy])
                self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return lm_list

    def get_gesture(self, lm_list):
        if not lm_list: return "NONE"
        
        # Pinch Detection (Thumb tip index 4, Index tip index 8)
        dist = math.hypot(lm_list[8][1] - lm_list[4][1], lm_list[8][2] - lm_list[4][2])
        
        # Finger statuses (8, 12, 16, 20 are tips)
        fingers = []
        for id in [8, 12, 16, 20]:
            if lm_list[id][2] < lm_list[id - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        if dist < 40: return "PINCH"
        if sum(fingers) == 4: return "OPEN"
        if sum(fingers) == 0: return "FIST"
        if sum(fingers) == 2 and fingers[0] == 1 and fingers[1] == 1: return "TWO"
        
        # SHAKA sign: Pinky is up, Index, Middle, Ring are down
        if fingers == [0, 0, 0, 1]: return "SHAKA"
        
        return "NEUTRAL"