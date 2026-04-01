import mediapipe as mp
import cv2

mp_hands = mp.solutions.hands

class HandTracker:
    def __init__(self):
        self.hands = mp_hands.Hands(max_num_hands=1)
        self.results = None

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)
        return self.results

    def close(self):
        self.hands.close()