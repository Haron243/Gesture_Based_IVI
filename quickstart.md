# 🚀 Quick Start Guide
## Get your Electrifex IVI System running in 5 minutes

---

## Prerequisites

✅ **Python 3.8+** installed  
✅ **Webcam** connected  
✅ **5 minutes** of your time  

---

## Installation (One-Time Setup)

### Step 1: Install Dependencies
```bash
pip install opencv-python mediapipe PyQt5 numpy
```

**Troubleshooting**: If you get errors, try:
```bash
pip install --upgrade pip
pip install opencv-python==4.8.1.78 mediapipe==0.10.9 PyQt5==5.15.10 numpy==1.24.3
```

---

## Running the Application

### Basic Launch
```bash
python main.py
```

That's it! The application will:
1. ✅ Start the gesture detection engine
2. ✅ Open the camera feed window
3. ✅ Display the main IVI interface

---

## First-Time Setup

When you first launch:

1. **Camera Permission**: Allow camera access when prompted
2. **Hand Detection**: Hold your hand in front of the camera
3. **Green Lines**: You'll see green hand skeleton tracking
4. **Confidence Bar**: Watch the blue bar at the top - it shows detection quality

---

## Your First Gesture

### Try the "Peace Sign" (2 fingers)
1. Hold up your **index and middle fingers**
2. Keep them **steady** for ~1 second
3. Watch the **T9 input** display show **"2"**
4. The contact list will filter to **ABC** contacts

**🎉 Congratulations!** You just made your first gesture!

---

## Common Gestures (Practice These)

| Show This | Result |
|-----------|--------|
| ✊ **Closed fist** | Digit **0** |
| ☝️ **One finger** | Digit **1** |
| ✌️ **Two fingers** | Digit **2** |
| 👌 **Pinch** (thumb+index touch) | **Select** current item |
| ✋ **Hand at top** of screen | **Scroll up** |
| 🤚 **Hand at bottom** of screen | **Scroll down** |

---

## Making Your First "Call"

### Method 1: T9 Search
1. Show **"5"** (all 4 fingers + thumb) → Filters to J, K, L
2. **Scroll** through contacts with hand at top/bottom
3. **Pinch** to "call" selected contact

### Method 2: Browse & Select
1. Hold hand in middle (neutral zone)
2. Move hand to **top** to scroll up
3. Move hand to **bottom** to scroll down
4. **Pinch** when you find the contact

---

## Customizing Your Experience

### Open Settings
1. Look at the **left sidebar**
2. Click **"SET"** button
3. Adjust:
   - **Hand mode** (right/left)
   - **Sensitivity**
   - **Voice feedback**
   - **High contrast mode**

---

## Tips for Best Performance

### ✅ DO:
- Use **good lighting** (bright but not direct sunlight)
- Keep hand **12-18 inches** from camera
- Hold gestures **steady** for 1 second
- Practice in the **"Gesture Map"** on the right panel

### ❌ DON'T:
- Wear **thick gloves**
- Make gestures while **steering** (safety first!)
- Rush - the system needs **stable** gestures
- Cover the camera

---

## Troubleshooting

### "No camera detected"
```bash
# Test camera manually
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```
If `False`, check:
- Camera is plugged in
- Camera permissions granted
- No other app is using camera

### "Gestures not detected"
- Check **confidence bar** (top right) - should be **blue/green**
- Improve **lighting**
- Move hand **closer** to camera
- Hold gesture **longer** (1-2 seconds)

### "System is slow"
```python
# In config.py, enable performance mode:
from config import Presets
Presets.apply_performance_mode()
```

### "Voice feedback not working"
- Check **Settings → Voice Feedback** is ON
- Test system audio is working
- Try adjusting volume

---

## Advanced Features (Once Comfortable)

### Swipe Navigation
- **Swipe right**: Jump to next letter (A→B→C)
- **Swipe left**: Jump to previous letter (Z→Y→X)

### Cancel Operation
- **Hold open palm** (all 5 fingers) for 1 second
- Clears current input and resets list

### Hang Up Call
- **Hold thumbs down** for 1.5 seconds
- Ends call and returns to main list

---

## Testing Your System

Run the performance test:
```bash
python test_metrics.py
```

This will:
- ✅ Simulate 100 gesture detections
- ✅ Measure accuracy and latency
- ✅ Generate performance report
- ✅ Check if system meets requirements

**Target metrics:**
- Latency: < 200ms
- Accuracy: > 90%
- Confidence: > 0.7

---

## Next Steps

### 1. **Train the Predictor**
The more you use it, the smarter it gets:
- System learns when you call certain people
- Favorites appear at top automatically
- Recent calls get priority

### 2. **Customize Gestures**
Edit `config.py` to adjust:
- Gesture sensitivity
- Cooldown times
- Zone boundaries
- T9 commit delay

### 3. **Enable Debug Mode**
```python
from config import Presets
Presets.apply_debug_mode()
```
Shows detailed metrics and performance data

---

## Daily Usage Pattern

**Morning commute:**
1. System predicts your common morning contacts
2. Use T9 to quickly filter
3. Pinch to dial

**Throughout day:**
1. System learns your patterns
2. Adapts suggestions based on time
3. Favorites always accessible

---

## Getting Help

### In-App Help
- Check **"Gesture Map"** panel (right side)
- Watch **confidence bar** for detection status
- Listen to **voice feedback**

### Debug Window
The camera feed window shows:
- ✅ **Green skeleton** = hand detected
- ✅ **Blue status text** = current gesture
- ✅ **Blue bar** = confidence level
- ❌ **Red zones** = scroll areas

### Error Messages
System will show colored notifications:
- 🟢 **Green** = Success (calling, selected)
- 🔴 **Red** = Disconnect/error
- 🟡 **Yellow** = Warning/timeout

---

## Performance Optimization

### For Raspberry Pi / Low-Power Devices:
```python
# In config.py
GestureConfig.MODEL_COMPLEXITY = 0
GestureConfig.FRAME_SKIP = 1
UIConfig.ENABLE_ANIMATIONS = False
```

### For Maximum Accuracy:
```python
# In config.py
GestureConfig.STABILITY_THRESHOLD = 8
GestureConfig.CONFIDENCE_THRESHOLD = 0.85
```

---

## Safety Reminder

⚠️ **IMPORTANT**: 
- Only use when **vehicle is stopped** or you have a **passenger** operating it
- Enable voice feedback to **minimize looking at screen**
- Pull over if you need extended interaction
- **Safety always comes first**

---

## What's Next?

Once comfortable, explore:
- 📊 **Metrics tracking** (`test_metrics.py`)
- 🧠 **Smart predictions** (`smart_predictor.py`)
- ⚙️ **Custom configuration** (`config.py`)
- 🎨 **UI customization** (edit styles in `main.py`)

---

## Support

**Issues?** Check:
1. Camera is working: `python -c "import cv2; cv2.VideoCapture(0).read()"`
2. Packages installed: `pip list | grep -E 'opencv|mediapipe|PyQt5'`
3. Python version: `python --version` (need 3.8+)

**Still stuck?** 
- Check error messages in terminal
- Enable debug mode: `Presets.apply_debug_mode()`
- Review performance metrics: `python test_metrics.py`

---

## Quick Reference Card

```
GESTURES CHEAT SHEET
━━━━━━━━━━━━━━━━━━━━
Digits: 0-9 fingers
Select: 👌 Pinch
Scroll: ✋ Hand top/bottom
Swipe: 👈👉 Quick movement
Cancel: ✋ Open palm (hold)
Hang up: 👎 Thumbs down (hold)

T9 KEYPAD
━━━━━━━━━━━━━━━━━━━━
2=ABC  3=DEF  4=GHI
5=JKL  6=MNO  7=PQRS
8=TUV  9=WXYZ 0=Space
```

Print this and keep it handy! 📋

---

**Ready to revolutionize your driving experience? Let's go! 🚗💨**
