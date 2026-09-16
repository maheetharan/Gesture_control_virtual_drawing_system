import mediapipe as mp
import cv2

mp_hands = mp.solutions.hands

class HandTracker:
    def __init__(self):
        self.hands = mp_hands.Hands(
            model_complexity=1, # 1 tracks much better at the edges (bottom of screen)
            max_num_hands=1,
            min_detection_confidence=0.5, # Lower confidence to prevent drops at bottom edge
            min_tracking_confidence=0.5
        )
        self.results = None

    def process(self, frame):
        # Pass the frame directly without squishing aspect ratio to prevent tracking loss
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)
        return self.results

    def close(self):
        self.hands.close()