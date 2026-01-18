
---

# 🚗 Electrifex IVI System v2.0

## Gesture-Based Smart Contact Navigation for Automotive Safety

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-orange.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15-red.svg)

An advanced hands-free infotainment system that enables drivers to navigate contacts and make calls using hand gestures detected by an in-cabin camera. Designed to minimize driver distraction while maintaining full control.

---

## 🎯 Key Features

### 🚀 New: Spatial T9 Typing

* Spatial Selection: Select letters by moving your hand Left, Center, or Right while holding a number
* Fist-to-Commit: Instantly type the selected letter by making a Fist (no waiting for timers)
* Fixed Zones: Visualized fixed zones on the camera feed for muscle-memory reliability

### ✋ Enhanced Gesture Recognition

* Euro-Style Counting: Distinct 1–9 numbering system using thumb states
* Zone-Based Scrolling: Move hand to top/bottom 20% of screen to scroll
* Pinch-to-Select: “OK” sign to confirm calls
* Safety Gestures:

  * 🤙 Shaka (Thumb + Pinky) → Cancel / Clear input
  * 👎✊ Thumbs Down + Fist → Disconnect / Hang up

### 🧠 Smart Contact Prediction

* AI-powered suggestions based on time, day, and frequency
* Favorites system with priority boosting
* Fuzzy matching for flexible name searching even with typos

---

## 📁 Project Structure

```text
electrifex-ivi/
├── gesture_engine.py        # Enhanced gesture detection (Spatial Logic)
├── main.py                  # Main IVI interface (PyQt5)
├── smart_predictor.py       # AI contact prediction system
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── contact_patterns.json    # Auto-generated user patterns
```

---

## 🚀 Installation

### 1. Clone the repository

git clone [https://github.com/Haron243/electrifex-ivi.git](https://github.com/Haron243/electrifex-ivi.git)
cd electrifex-ivi

### 2. Install dependencies

pip install -r requirements.txt

### 3. Run the application

python main.py

---

## 🎮 Gesture Guide

### Number Gestures (Inputs)

| Number | Gesture | T9 Letters |
| :--- | :--- | :--- |
| **1** | Index Finger Up | BACKSPACE |
| **2** | Index + Middle | A, B, C |
| **3** | Index + Middle + Ring | D, E, F |
| **4** | Four Fingers | G, H, I |
| **5** | Open Palm | J, K, L |
| **6** | Thumb Only (👍) | M, N, O |
| **7** | Thumb + Index | P, Q, R, S |
| **8** | Thumb + Index + Middle | T, U, V |
| **9** | Thumb + Index + Middle + Ring | W, X, Y, Z |
| **0** | Closed Fist (✊) | COMMIT / ENTER |

---

### Control Gestures

| Gesture | Action | Description |
| :--- | :--- | :--- |
| **Pinch** (👌) | Select | Call selected contact |
| **Shaka** (🤙) | Cancel | Clear input/search |
| **Thumbs Down + Fist** | Hang Up | Disconnect active call |
| **Hand High** | Scroll Up | Move hand to top 20% of frame |
| **Hand Low** | Scroll Down | Move hand to bottom 20% of frame |

---

## 🖐️ How to Type (Spatial T9)

Typing is a fast 3-step process. No multi-tap required.

Example: Typing the letter “A” (from key 2)

1. HOLD
   Show 2 fingers (Index + Middle)
   UI shows: A | B | C

2. MOVE
   Move your hand to the LEFT side of the frame
   UI highlights: A

3. COMMIT
   Close your hand into a FIST
   System types: A

Zone Mapping:

* Left Zone: 1st letter (A, D, G…)
* Center Zone: 2nd letter (B, E, H…)
* Right Zone: 3rd letter (C, F, I…)
* Far Right Zone: 4th letters (keys 7 and 9)

---

## 🎬 Usage Workflow

### Making a Call

1. Search
   Use Spatial T9 to type the first letter
   Example: “Mom” → Hold 6 (MNO) → Move Left → Fist

2. Refine
   Type additional letters if needed

3. Scroll
   Move hand down to browse contacts

4. Call
   Pinch (👌) to dial

5. End Call
   Thumbs down (👎) + Fist

---

## ⚙️ Settings & Customization

Access via the SET button:

* Hand Mode (Left / Right)
* Gesture Sensitivity
* Voice Feedback (TTS)
* High Contrast Mode (Daylight driving)

---

## 📊 Performance Metrics

Displayed in console on exit:

* Detection accuracy
* Average confidence score
* Frames Per Second (FPS)

---

## 📝 License

Developed for the HackEFX Automotive Innovation Challenge.

---

## 🙏 Acknowledgments

MediaPipe – Hand tracking framework
OpenCV – Computer vision tools
PyQt5 – Professional UI framework

---

## 📧 Contact

Email: [haronmalayil@gmail.com](mailto:haronmalayil@gmail.com)
GitHub: [https://github.com/Haron243](https://github.com/Haron243)

---

⚠️ Safety Notice
This system is designed to minimize distraction. Always prioritize road safety and use voice commands whenever possible.

---
