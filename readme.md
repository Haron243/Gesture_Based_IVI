# 🚗 Electrifex IVI System v2.0
## Gesture-Based Smart Contact Navigation for Automotive Safety

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-orange.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15-red.svg)

An advanced hands-free infotainment system that enables drivers to navigate contacts and make calls using **hand gestures** detected by an in-cabin camera. Designed to minimize driver distraction while maintaining full control.

---

## 🎯 Key Features

### Enhanced Gesture Recognition
- **10 Numeric Gestures** (0-9) with T9-style keypad mapping
- **Pinch-to-Select** for confirming actions
- **Swipe Gestures** for fast alphabet navigation (A→B→C...)
- **Hold Gestures**:
  - Open palm hold → Cancel operation
  - Thumbs down hold → Disconnect/hang up call
- **Zone-Based Scrolling** (top/bottom screen zones)
- **Real-time confidence scoring** with visual feedback

### Smart Contact Prediction
- **AI-powered suggestions** based on:
  - Time of day patterns
  - Day of week patterns
  - Call frequency and recency
  - Average call duration
  - Location context (optional)
- **Favorites system** with priority boosting
- **Fuzzy matching** for flexible name search

### Safety-First UX
- **Voice feedback** for eyes-free confirmation
- **Minimal visual distraction** design
- **Large touch targets** optimized for in-vehicle use
- **High contrast mode** for bright daylight
- **Adaptive brightness** for varying lighting conditions
- **Sub-200ms latency** for responsive feel

### Customization
- **Left/right hand mode** support
- **Adjustable sensitivity** settings
- **Configurable cooldown periods**
- **Voice feedback toggle**
- **Dark/High-contrast themes**

---

## 📁 Project Structure

```
electrifex-ivi/
├── gesture_engine.py        # Enhanced gesture detection core
├── main.py                   # Main IVI interface
├── smart_predictor.py        # AI contact prediction system
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── contact_patterns.json     # Auto-generated user patterns (created at runtime)
```

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/electrifex-ivi.git
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

| Gesture | Action | How To |
|---------|--------|--------|
| **0-9 Fingers** | T9 Input | Hold up corresponding number of fingers |
| **Pinch** (Thumb + Index) | Select/Confirm | Touch thumb tip to index finger tip |
| **Hand at Top** | Scroll Up | Move wrist above top zone line |
| **Hand at Bottom** | Scroll Down | Move wrist below bottom zone line |
| **Swipe Right** | Next Letter (A→B) | Quick horizontal hand movement right |
| **Swipe Left** | Previous Letter (Z→Y) | Quick horizontal hand movement left |
| **Open Palm Hold** (1s) | Cancel/Clear | All five fingers extended, hold steady |
| **Thumbs Down Hold** (1.5s) | Disconnect Call | Thumb down, fingers up, hold steady |

### T9 Keypad Mapping
```
1 = [Clear/Backspace]
2 = ABC    3 = DEF
4 = GHI    5 = JKL    6 = MNO
7 = PQRS   8 = TUV    9 = WXYZ
0 = Space
```

**Example**: To type "HELLO":
1. Show **4** (GHI) → tap twice → **H**
2. Show **3** (DEF) → tap twice → **E**
3. Show **5** (JKL) → tap once → **L**
4. Show **5** (JKL) → tap once → **L**
5. Show **6** (MNO) → tap three times → **O**

---

## 🎬 Usage Workflow

### Making a Call
1. **Filter contacts** using T9 gestures (e.g., "5" → shows contacts starting with J, K, L)
2. **Scroll** through filtered list using zone scrolling or swipes
3. **Pinch** to select and initiate call
4. **Thumbs down** to hang up when done

### Quick Actions
- **Swipe** to jump between alphabet sections
- **Open palm** to cancel current input and return to full contact list
- **Favorites** appear at top with ⭐ indicator
- **Recent calls** show with 🕒 indicator

---

## ⚙️ Settings & Customization

Access settings via the **"SET"** button in the sidebar:

- **Hand Mode**: Switch between right/left hand preference
- **Gesture Sensitivity**: Adjust detection threshold (0.5x - 1.5x)
- **Voice Feedback**: Enable/disable audio confirmations
- **High Contrast**: Toggle enhanced visibility for daylight

---

## 🧠 Smart Prediction System

The system learns from your usage patterns:

### What It Tracks
- **Time patterns** (Who you call at what time)
- **Day patterns** (Who you call on which days)
- **Frequency** (How often you call someone)
- **Recency** (When you last called)
- **Duration** (Average call length)
- **Location** (Optional: where you were when calling)

### How It Helps
- **Auto-prioritizes** likely contacts at the top
- **Reduces gestures** needed to reach frequent contacts
- **Adapts** to your daily routine
- **Explains** why contacts are suggested

**Example**: If you call your boss every weekday morning at 9 AM from the office, the system will automatically prioritize them during those times.

---

## 📊 Performance Metrics

The system tracks and displays:
- **Detection accuracy** (% of correct gesture recognitions)
- **Average confidence score** (gesture stability)
- **Frame rate** (processing speed)
- **False positive rate** (unwanted detections)

View metrics in terminal when closing the application.

---

## 🔧 Technical Details

### Architecture
- **Gesture Engine** (`gesture_engine.py`): MediaPipe-based hand tracking with confidence scoring
- **UI Layer** (`main.py`): PyQt5 interface optimized for automotive displays
- **AI Predictor** (`smart_predictor.py`): Pattern learning and contact ranking system

### Key Algorithms
1. **Gesture Stability**: Multi-frame validation to reject transient movements
2. **Zone Locking**: Prevents accidental scrolling during intentional gestures
3. **Adaptive Timing**: Smart cooldowns that balance responsiveness vs reliability
4. **Fuzzy Matching**: Handles imperfect T9 input gracefully

### Performance Optimizations
- **Model Complexity**: Balanced between accuracy (1) and speed
- **Frame Buffering**: Reduces processing overhead
- **Brightness Normalization**: Adapts to lighting conditions automatically
- **Efficient State Management**: Minimal memory footprint

---

## 🎯 Evaluation Against Project Goals

| Milestone | Status | Notes |
|-----------|--------|-------|
| **Hand Detection** | ✅ Complete | Stable tracking under varying conditions |
| **Gesture Classification** | ✅ Complete | 0-9 + 5 special gestures with confidence scoring |
| **Temporal Sequencing** | ✅ Complete | T9 multi-tap with auto-commit timing |
| **IVI Integration** | ✅ Complete | Full contact navigation + smart predictions |
| **Safety UX** | ✅ Complete | Voice feedback, minimal distraction design |
| **Latency** | ✅ <200ms | Typically 50-100ms end-to-end |

---

## 🐛 Known Limitations

1. **Lighting**: Very dim (<20 lux) or very bright (direct sunlight) conditions may reduce accuracy
2. **Hand Size**: Optimized for adult hands; children may need recalibration
3. **Gloves**: Thick gloves interfere with finger detection
4. **Multitasking**: System assumes driver is not actively steering during gesture input
5. **Camera Position**: Requires clear view of driver's hand workspace

---

## 🚀 Future Enhancements

### Planned Features
- [ ] **ML Gesture Model**: Train custom CNN for user-specific gestures
- [ ] **Multi-Language T9**: Support for non-English contact names
- [ ] **Context Awareness**: GPS integration for location-based predictions
- [ ] **Voice Commands**: Hybrid gesture + voice control
- [ ] **Driver Monitoring**: Attention detection for safety warnings
- [ ] **Gesture Macros**: Custom multi-gesture sequences for power users
- [ ] **Cloud Sync**: Backup patterns across vehicles

### Research Directions
- [ ] **Depth Sensing**: Use 3D cameras for more robust detection
- [ ] **Eye Tracking**: Gaze-based contact selection
- [ ] **Haptic Feedback**: Steering wheel vibration on gesture recognition
- [ ] **Thermal Imaging**: Night-time gesture detection

---

## 📝 License

This project is developed for the **HackEFX** automotive innovation challenge.

---

## 🙏 Acknowledgments

- **MediaPipe** for the excellent hand tracking framework
- **OpenCV** for computer vision tools
- **PyQt5** for the professional UI framework
- **HackEFX** for the challenge inspiration

---

## 📧 Contact

For questions, suggestions, or collaboration:
- **Email**: your.email@example.com
- **GitHub**: [@yourusername](https://github.com/yourusername)

---

## 🎥 Demo Video

[Link to demonstration video showing system in action]

---

**⚠️ Safety Notice**: This system is designed to minimize distraction, but drivers should always prioritize road safety. Use voice commands when possible and only interact with the system when safe to do so.

---

**Built with ❤️ for safer driving experiences**
