# 🎨 Gesture Control Virtual Drawing System

Draw on your screen using just your hand — no mouse, no touch screen needed! This app uses your webcam to detect hand gestures in real-time and lets you paint virtually in the air.

---

## 📸 Demo
<img width="1828" height="1012" alt="Screenshot 2026-05-23 164254" src="https://github.com/user-attachments/assets/23c2f3fe-e99e-448a-90f4-52d9c9b67c02" />
<img width="1849" height="986" alt="Screenshot 2026-05-23 164609" src="https://github.com/user-attachments/assets/a169c23e-9c22-45a0-a0eb-dc102f6452e9" />


---

## ✨ Features

- ✋ Real-time hand tracking using webcam
- 🎨 Multiple brush types and colors
- 🖐️ Gesture-based controls (raise fingers to switch modes)
- 🧹 Clear canvas with a gesture
- ⚡ Optimized for low lag with async processing
- 🌐 Flask web streaming version included

---

## 🛠️ Tech Stack

| Technology | Usage |
|------------|-------|
| Python | Core programming language |
| OpenCV | Video capture & image processing |
| MediaPipe | Hand landmark detection |
| Flask | Web streaming version |
| NumPy | Array & frame manipulation |

---

## 📦 Installation

1. Clone the repository
```bash
git clone https://github.com/maheetharan/Gesture_control_virtual_drawing_system.git
cd Gesture_control_virtual_drawing_system
```

2. Install dependencies
```bash
pip install opencv-python mediapipe flask numpy
```

3. Run the app
```bash
python main.py
```

---

## 🖐️ How to Use

| Gesture | Action |
|---------|--------|
| Index finger up | Draw mode |
| Index + Middle finger up | Move / Select mode |
| All fingers up | Clear canvas |
| Thumb up | Change color |

---

## 👨‍💻 Author

**Maheetharan**
- GitHub: [@maheetharan](https://github.com/maheetharan)
- LinkedIn: [Your LinkedIn]
- B.Tech AI & Data Science, Kamaraj College of Engineering & Technology

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).
