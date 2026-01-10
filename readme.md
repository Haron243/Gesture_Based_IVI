Based on the latest code you provided (Fixed Center Zones, Fist-to-Commit, Shaka for Cancel), here is the updated **README.md**.

I have updated the **Gesture Guide**, **Usage Workflow**, and **Key Features** sections to accurately reflect your new Spatial T9 system.

```markdown
# 🚗 Electrifex IVI System v2.0
## Gesture-Based Smart Contact Navigation for Automotive Safety

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-orange.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15-red.svg)

An advanced hands-free infotainment system that enables drivers to navigate contacts and make calls using **hand gestures** detected by an in-cabin camera. Designed to minimize driver distraction while maintaining full control.

---

## 🎯 Key Features

### 🚀 New: Spatial T9 Typing
- **Spatial Selection**: Select letters by moving your hand **Left, Center, or Right** while holding a number.
- **Fist-to-Commit**: Instantly type the selected letter by making a **Fist** (no waiting for timers).
- **Fixed Zones**: Visualized fixed zones on the camera feed for muscle-memory reliability.

### Enhanced Gesture Recognition
- **Euro-Style Counting**: Distinct 1-9 numbering system using thumb states.
- **Zone-Based Scrolling**: Move hand to top/bottom 20% of screen to scroll.
- **Pinch-to-Select**: "OK" sign to confirm calls.
- **Safety Gestures**:
  - 🤙 **Shaka** (Thumb+Pinky) → Cancel/Clear input.
  - 👎✊ **Thumbs Down + Fist** → Disconnect/Hang up (prevents accidental triggers).

### Smart Contact Prediction
- **AI-powered suggestions** based on time, day, and frequency.
- **Favorites system** with priority boosting.
- **Fuzzy matching** allows for flexible name searching even with typos.

---

## 📁 Project Structure


```

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
```bash
git clone [https://github.com/Haron243/electrifex-ivi.git](https://github.com/Haron243/electrifex-ivi.git)
cd electrifex-ivi

```

### 2. Install dependencies

```bash
pip install -r requirements.txt

```

### 3. Run the application

```bash
python main.py

```

---

## 🎮 Gesture Guide

### 1. The Numbers (Inputs)

| Number | Gesture | T9 Letters |
| --- | --- | --- |
| **1** | Index Finger Up | **BACKSPACE** |
| **2** | Index + Middle | A, B, C |
| **3** | Index + Mid + Ring | D, E, F |
| **4** | Four Fingers | G, H, I |
| **5** | All 5 Fingers (Open Palm) | J, K, L |
| **6** | Thumb Only (👍) | M, N, O |
| **7** | Thumb + Index | P, Q, R, S |
| **8** | Thumb + Index + Middle | T, U, V |
| **9** | Thumb + Index + Mid + Ring | W, X, Y, Z |
| **0** | **CLOSED FIST** (✊) | **COMMIT / ENTER** |

### 2. Control Gestures

| Gesture | Action | Description |
| --- | --- | --- |
| **Pinch** (👌) | **Select** | Pinch Index & Thumb to call selected contact. |
| **Shaka** (🤙) | **Cancel** | Thumb & Pinky out. Clears input/search. |
| **Thumbs Down + Fist** | **Hang Up** | Thumb down, fingers curled. Disconnects call. |
| **Hand High** | **Scroll Up** | Move wrist to top 20% of frame. |
| **Hand Low** | **Scroll Down** | Move wrist to bottom 20% of frame. |

---

## 🖐️ How to Type (Spatial T9)

Typing is a fast, 3-step process. You do not need to "multi-tap".

**Example: To type the letter "A" (First letter of key '2'):**

1. **HOLD**: Show **2 Fingers** (Index + Middle).
* *UI shows: A | B | C*


2. **MOVE**: Move your hand to the **LEFT** side of the frame.
* *UI Highlights: [ A ]*


3. **COMMIT**: Close your hand into a **FIST**.
* *System types: "A"*



**Zone Mapping:**

* **Left Zone**: 1st Letter (e.g., A, D, G...)
* **Center Zone**: 2nd Letter (e.g., B, E, H...)
* **Right Zone**: 3rd Letter (e.g., C, F, I...)
* *(Far Right Zone used for 4th letters on keys 7 & 9)*

---

## 🎬 Usage Workflow

### Making a Call

1. **Search**: Use the Spatial T9 method to type the first letter of the name.
* *Example: To find "Mom", hold '6' (MNO) -> Move Left -> Make Fist.*


2. **Refine**: If needed, type the second letter.
3. **Scroll**: If the contact isn't selected, move hand down to scroll.
4. **Call**: Pinch (👌) to dial.
5. **End**: Thumbs down (👎) with a fist to hang up.

---

## ⚙️ Settings & Customization

Access settings via the **"SET"** button in the sidebar:

* **Hand Mode**: Switch between right/left hand preference (mirrors gestures).
* **Gesture Sensitivity**: Adjust detection threshold.
* **Voice Feedback**: Enable/disable TTS audio confirmations.
* **High Contrast**: Toggle enhanced visibility for daylight driving.

---

## 📊 Performance Metrics

The system tracks metrics in real-time. View the console output upon closing the app for a detailed report:

* **Detection accuracy**
* **Average confidence score**
* **FPS (Frames Per Second)**

---

## 📝 License

This project is developed for the **HackEFX** automotive innovation challenge.

---

## 🙏 Acknowledgments

* **MediaPipe** for the excellent hand tracking framework.
* **OpenCV** for computer vision tools.
* **PyQt5** for the professional UI framework.

---

## 📧 Contact

For questions, suggestions, or collaboration:

* **Email**: haronmalayil@gmail.com
* **GitHub**: [@Haron243](https://github.com/Haron243)

---

**⚠️ Safety Notice**: This system is designed to minimize distraction, but drivers should always prioritize road safety. Use voice commands when possible and only interact with the system when safe to do so.

```

```