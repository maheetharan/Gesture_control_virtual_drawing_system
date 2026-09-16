import cv2
import numpy as np
import os
from gesture_module import GestureController
from puzzle_module import create_puzzle
from utils import draw_ui_panel # Assuming you have the UI logic here

# Settings
WIDTH, HEIGHT = 1280, 720
GRID_SIZE = 3

class AnimePuzzleGame:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, WIDTH)
        self.cap.set(4, HEIGHT)
        self.detector = GestureController()
        self.score = 0
        self.pieces = []
        self.selected_piece = None
        self.mode = "CAMERA"
        self.shaka_counter = 0

    def run(self):
        while True:
            success, frame = self.cap.read()
            if not success: break
            
            frame = cv2.flip(frame, 1)
            clean_frame = frame.copy()
            
            lm_list = self.detector.get_landmarks(frame)
            gesture = self.detector.get_gesture(lm_list)

            if self.mode == "CAMERA":
                cv2.putText(frame, "Show TWO fingers to take a photo!", (50, 50), 1, 2, (0, 255, 0), 2)
                cv2.putText(frame, f"Score: {self.score}", (1100, 50), 1, 2, (0, 255, 255), 2)
                cv2.putText(frame, f"Gesture: {gesture}", (50, 680), 1, 2, (255, 255, 255), 2)
                
                # Draw a guide square where the photo will be taken from
                h, w, _ = clean_frame.shape
                size = min(h, w)
                y1, y2 = (h - size) // 2, (h + size) // 2
                x1, x2 = (w - size) // 2, (w + size) // 2
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
                
                if gesture == "TWO":
                    cropped = clean_frame[y1:y2, x1:x2]
                    img = cv2.resize(cropped, (450, 450))
                    self.pieces = create_puzzle(img, grid_size=GRID_SIZE, offset_x=800, offset_y=150)
                    self.selected_piece = None
                    self.mode = "PUZZLE"
                    
                    cv2.putText(frame, "SNAP!", (x1 + size//2 - 100, y1 + size//2), 1, 4, (0, 255, 255), 4)
                    cv2.imshow("Game", frame)
                    cv2.waitKey(500)
                    continue

            elif self.mode == "PUZZLE":
                # Draw the 3x3 Target Grid Frame on the right
                for i in range(GRID_SIZE + 1):
                    # Horizontal lines
                    cv2.line(frame, (800, 150 + i*150), (1250, 150 + i*150), (0, 255, 0), 2)
                    # Vertical lines
                    cv2.line(frame, (800 + i*150, 150), (800 + i*150, 600), (0, 255, 0), 2)

                # Interaction Logic
                if gesture == "SHAKA":
                    self.shaka_counter += 1
                    cv2.putText(frame, f"Hold SHAKA to Retake: {self.shaka_counter}/10", (400, 300), 1, 2, (0, 0, 255), 3)
                    if self.shaka_counter >= 10:
                        self.mode = "CAMERA"
                        self.pieces = []
                        self.selected_piece = None
                        self.shaka_counter = 0
                        continue
                else:
                    self.shaka_counter = 0

                if gesture == "PINCH" and lm_list:
                    cx, cy = lm_list[8][1], lm_list[8][2] # Index finger tip
                    if self.selected_piece is None:
                        for p in self.pieces:
                            if not p.is_locked and p.pos[0] < cx < p.pos[0]+p.size and p.pos[1] < cy < p.pos[1]+p.size:
                                self.selected_piece = p
                                break
                    if self.selected_piece:
                        self.selected_piece.update_pos(cx, cy)
                        # Automatically snap if close enough during drag
                        if self.selected_piece.check_snap():
                            self.selected_piece = None
                
                elif gesture in ["FIST", "OPEN"]:
                    if self.selected_piece:
                        self.selected_piece.check_snap()
                        self.selected_piece = None

                # Render All Pieces
                locked_count = 0
                for p in self.pieces:
                    x, y = p.pos
                    # Ensure piece doesn't go off-screen during drag to avoid crash
                    if 0 <= y < HEIGHT - p.size and 0 <= x < WIDTH - p.size:
                        frame[y:y+p.size, x:x+p.size] = p.img
                    
                    if p.is_locked: 
                        locked_count += 1
                    
                    # Highlight selected piece
                    if p == self.selected_piece:
                        cv2.rectangle(frame, (x, y), (x+p.size, y+p.size), (0, 255, 255), 3)

                # UI Display (Score and Gesture)
                cv2.putText(frame, "Show SHAKA (Thumb & Pinky) to retake photo", (50, 50), 1, 2, (0, 0, 255), 2)
                cv2.putText(frame, f"Score: {self.score}", (1100, 50), 1, 2, (0, 255, 255), 2)
                cv2.putText(frame, f"Gesture: {gesture}", (50, 680), 1, 2, (255, 255, 255), 2)

                # Check if Puzzle is Complete
                if locked_count == GRID_SIZE**2 and self.pieces:
                    self.score += 1
                    cv2.putText(frame, "PUZZLE COMPLETE!", (450, 360), 1, 4, (0, 255, 0), 4)
                    cv2.imshow("Game", frame)
                    cv2.waitKey(2000)
                    self.mode = "CAMERA"
                    self.pieces = []
                    continue

            cv2.imshow("Game", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    game = AnimePuzzleGame()
    game.run()