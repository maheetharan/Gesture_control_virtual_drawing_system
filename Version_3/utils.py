import cv2
import numpy as np
import requests
import os

def download_anime_image(character_name, save_path):
    """
    Optional: Fetches a character image from Jikan API if not found locally.
    """
    if os.path.exists(save_path):
        return cv2.imread(save_path)
    
    # Placeholder search logic (Simulating API fetch for Expo)
    print(f"Downloading {character_name} image...")
    # In a real scenario, use requests to hit https://api.jikan.moe/v4/characters
    # For now, we return a high-quality placeholder if the file is missing
    dummy_img = np.zeros((400, 400, 3), np.uint8)
    cv2.putText(dummy_img, character_name, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return dummy_img

def resize_and_pad(image, size=(450, 450)):
    """
    Resizes image to fit the 3x3 grid (150x150 per piece).
    """
    return cv2.resize(image, size)

def draw_ui_panel(frame, character_name, score, fps, gesture):
    """
    Draws a modern dark-themed UI overlay on the camera feed.
    """
    # 1. Top Bar Background (Translucent Black)
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (1280, 80), (20, 20, 20), -1)
    
    # 2. Bottom Instructions Background
    cv2.rectangle(overlay, (0, 650), (1280, 720), (20, 20, 20), -1)
    
    # Apply transparency
    alpha = 0.7
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # 3. Add Text Elements
    # Character Name (Top Left)
    cv2.putText(frame, f"TARGET: {character_name.upper()}", (30, 50), 
                cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 255), 2)
    
    # Score (Top Right)
    cv2.putText(frame, f"SCORE: {score}", (1050, 50), 
                cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)

    # FPS (Top Center)
    cv2.putText(frame, f"FPS: {int(fps)}", (600, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

    # Gesture Help (Bottom Center)
    help_text = f"GESTURE: {gesture}  |  PINCH TO GRAB  |  FIST TO DROP"
    cv2.putText(frame, help_text, (320, 695), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

def show_victory_effect(frame):
    """
    Creates a simple 'Flash' effect when a piece snaps correctly.
    """
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (1280, 720), (0, 255, 0), -1)
    cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)