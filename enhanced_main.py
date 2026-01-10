import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QLabel, QFrame, QGridLayout,
                             QPushButton, QSlider, QComboBox, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtTextToSpeech import QTextToSpeech
import time
from gesture_engine import GestureEngine
import difflib

class SettingsDialog(QDialog):
    """Settings panel for gesture customization"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gesture Settings")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Hand Mode
        hand_layout = QHBoxLayout()
        hand_layout.addWidget(QLabel("Hand Mode:"))
        self.hand_combo = QComboBox()
        self.hand_combo.addItems(["Right Hand", "Left Hand"])
        hand_layout.addWidget(self.hand_combo)
        layout.addLayout(hand_layout)
        
        # Sensitivity
        sens_layout = QVBoxLayout()
        sens_layout.addWidget(QLabel("Gesture Sensitivity:"))
        self.sens_slider = QSlider(Qt.Horizontal)
        self.sens_slider.setRange(50, 150)
        self.sens_slider.setValue(100)
        self.sens_label = QLabel("Normal (1.0x)")
        self.sens_slider.valueChanged.connect(self.update_sens_label)
        sens_layout.addWidget(self.sens_slider)
        sens_layout.addWidget(self.sens_label)
        layout.addLayout(sens_layout)
        
        # Voice Feedback
        voice_layout = QHBoxLayout()
        self.voice_check = QPushButton("Voice Feedback: ON")
        self.voice_check.setCheckable(True)
        self.voice_check.setChecked(True)
        self.voice_check.clicked.connect(self.toggle_voice)
        voice_layout.addWidget(self.voice_check)
        layout.addLayout(voice_layout)
        
        # High Contrast Mode
        contrast_layout = QHBoxLayout()
        self.contrast_check = QPushButton("High Contrast: OFF")
        self.contrast_check.setCheckable(True)
        self.contrast_check.clicked.connect(self.toggle_contrast)
        contrast_layout.addWidget(self.contrast_check)
        layout.addLayout(contrast_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setStyleSheet("""
            QDialog { background-color: #1E1E1E; }
            QLabel { color: #FFF; font-size: 14px; }
            QComboBox, QPushButton { 
                background-color: #333; 
                color: #FFF; 
                border: 1px solid #555;
                padding: 8px;
                border-radius: 5px;
            }
            QSlider::groove:horizontal {
                background: #333;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00E5FF;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
    
    def update_sens_label(self, value):
        sens = value / 100.0
        self.sens_label.setText(f"Sensitivity: {sens:.1f}x")
    
    def toggle_voice(self):
        state = "ON" if self.voice_check.isChecked() else "OFF"
        self.voice_check.setText(f"Voice Feedback: {state}")
    
    def toggle_contrast(self):
        state = "ON" if self.contrast_check.isChecked() else "OFF"
        self.contrast_check.setText(f"High Contrast: {state}")
    
    def get_settings(self):
        return {
            'hand_mode': 'right' if self.hand_combo.currentIndex() == 0 else 'left',
            'sensitivity': self.sens_slider.value() / 100.0,
            'voice_enabled': self.voice_check.isChecked(),
            'high_contrast': self.contrast_check.isChecked()
        }

class ModernCarDisplay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Electrifex IVI - Spatial T9 (Fist Commit)")
        self.setGeometry(100, 100, 1280, 720)
        
        # --- DATA ---
        self.all_contacts = [
            "Aaron Smith", "Adam Driver", "Alice Johnson", "Ben Affleck", 
            "Brian O'Conner", "Charlie Puth", "Chris Evans", "Daniel Craig", 
            "David Beckham", "Electrifex Support", "Elon Musk", "Frank Ocean",
            "George Clooney", "Harry Styles", "Henry Cavill", "Ian Somerhalder",
            "Jack Sparrow", "Jason Statham", "Kevin Hart", "Liam Neeson",
            "Luke Skywalker", "Maria Garcia", "Nicole Kidman", "Oscar Isaac",
            "Paul Rudd", "Quinn Fabray", "Ryan Reynolds", "Sarah Connor",
            "Tom Hanks", "Uma Thurman", "Victor Stone", "Walter White",
            "Xavier Institute", "Yara Shahidi", "Zendaya", "Zac Efron"
        ]
        
        # T9-style keypad mapping
        self.T9_MAP = {
            '2': 'ABC', '3': 'DEF', '4': 'GHI',
            '5': 'JKL', '6': 'MNO', '7': 'PQRS',
            '8': 'TUV', '9': 'WXYZ', '0': ' '
        }
        
        self.current_filter = ""
        self.input_buffer = ""
        self.last_input_time = time.time()
        
        # SPATIAL STATE
        self.current_digit_held = None
        self.current_spatial_index = 1 # 0=Left, 1=Center, 2=Right
        self.spatial_letters = ""
        
        # Settings
        self.settings = {
            'hand_mode': 'right',
            'sensitivity': 1.0,
            'voice_enabled': True,
            'high_contrast': False
        }
        
        # Voice feedback
        self.tts = QTextToSpeech()
        self.tts.setRate(0.2)  # Slightly faster speech
        
        # Call history
        self.call_history = {}
        self.favorites = ["Electrifex Support", "Elon Musk"]
        
        # Input Timeout Check
        self.input_timer = QTimer()
        self.input_timer.timeout.connect(self.check_input_timeout)
        self.input_timer.start(200)

        # Clock Timer
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        
        self.init_ui()
        self.apply_styles()
        
        # --- START GESTURE ENGINE ---
        self.start_engine()

    def start_engine(self):
        """Helper to start/restart engine with connections"""
        if hasattr(self, 'engine'):
            self.engine.stop()
            
        self.engine = GestureEngine(self.settings)
        self.engine.gesture_detected.connect(self.handle_digit_input)
        self.engine.spatial_update.connect(self.handle_spatial_update) # Connect Spatial Updates
        self.engine.spatial_commit.connect(self.handle_spatial_commit) # Connect Fist Commit
        self.engine.scroll_detected.connect(self.handle_scroll)
        self.engine.select_detected.connect(self.handle_selection)
        self.engine.disconnect_detected.connect(self.handle_disconnect)
        self.engine.swipe_detected.connect(self.handle_swipe)
        self.engine.cancel_detected.connect(self.handle_cancel)
        self.engine.confidence_update.connect(self.update_confidence_bar)
        self.engine.start()

    def closeEvent(self, event):
        if hasattr(self, 'engine'):
            self.engine.stop()
        event.accept()

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        
        main_h_layout = QHBoxLayout(central_widget)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(0)

        # --- SIDEBAR ---
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(100)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 30, 0, 30)
        side_layout.setSpacing(40)

        for icon_text, active in [("NAV", False), ("MEDIA", False), ("PHONE", True), ("SET", False)]:
            btn = QLabel(icon_text)
            btn.setAlignment(Qt.AlignCenter)
            btn.setObjectName("SideBtn_Active" if active else "SideBtn")
            btn.setFixedHeight(60)
            if icon_text == "SET":
                btn.mousePressEvent = lambda e: self.open_settings()
            side_layout.addWidget(btn)
        
        side_layout.addStretch()
        main_h_layout.addWidget(sidebar)

        # --- CONTENT AREA ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 20, 30, 20)
        
        # STATUS BAR
        status_bar = QHBoxLayout()
        self.clock_label = QLabel("12:00 PM")
        self.clock_label.setObjectName("StatusBarText")
        
        self.confidence_bar = QLabel("")
        self.confidence_bar.setFixedWidth(100)
        self.confidence_bar.setFixedHeight(8)
        self.confidence_bar.setObjectName("ConfidenceBar")
        
        temp_label = QLabel("24°C  |  5G")
        temp_label.setObjectName("StatusBarText")
        status_bar.addWidget(self.clock_label)
        status_bar.addWidget(self.confidence_bar)
        status_bar.addStretch()
        status_bar.addWidget(temp_label)
        content_layout.addLayout(status_bar)

        # SPLIT LAYOUT
        split_layout = QHBoxLayout()
        split_layout.setSpacing(30)
        
        # LEFT: Contact List
        list_container = QFrame()
        list_container.setObjectName("ListContainer")
        list_layout = QVBoxLayout(list_container)
        
        header_row = QHBoxLayout()
        lbl_title = QLabel("Smart Contacts")
        lbl_title.setObjectName("SectionTitle")
        
        self.input_hud = QLabel("T9: Ready")
        self.input_hud.setObjectName("InputHUD")
        self.input_hud.setAlignment(Qt.AlignCenter)
        self.input_hud.setFixedWidth(200)
        
        header_row.addWidget(lbl_title)
        header_row.addStretch()
        header_row.addWidget(self.input_hud)
        list_layout.addLayout(header_row)

        self.contact_list = QListWidget()
        self.contact_list.setObjectName("ModernList")
        self.update_contact_list()
        list_layout.addWidget(self.contact_list)
        
        split_layout.addWidget(list_container, 60)

        # RIGHT: Enhanced Helper Widget
        helper_container = QFrame()
        helper_container.setObjectName("HelperWidget")
        helper_layout = QVBoxLayout(helper_container)
        helper_layout.setContentsMargins(20, 20, 20, 20)
        
        helper_title = QLabel("SPATIAL T9")
        helper_title.setAlignment(Qt.AlignCenter)
        helper_title.setObjectName("HelperTitle")
        helper_layout.addWidget(helper_title)

        # --- SPATIAL ZONES VISUALIZER ---
        zones_layout = QHBoxLayout()
        self.zone_labels = []
        for i in range(3): # 3 Zones (Left, Center, Right)
            z = QLabel("-")
            z.setAlignment(Qt.AlignCenter)
            z.setObjectName("ZoneLabel")
            z.setFixedHeight(80)
            self.zone_labels.append(z)
            zones_layout.addWidget(z)
        
        helper_layout.addLayout(zones_layout)
        
        # T9 Grid
        grid = QGridLayout()
        grid.setSpacing(12)
        
        t9_keys = [
            ('1', ''), ('2', 'ABC'), ('3', 'DEF'),
            ('4', 'GHI'), ('5', 'JKL'), ('6', 'MNO'),
            ('7', 'PQRS'), ('8', 'TUV'), ('9', 'WXYZ')
        ]
        
        r, c = 0, 0
        for num, letters in t9_keys:
            key_widget = QWidget()
            key_layout = QVBoxLayout(key_widget)
            key_layout.setContentsMargins(5, 5, 5, 5)
            key_layout.setSpacing(0)
            
            num_lbl = QLabel(num)
            num_lbl.setAlignment(Qt.AlignCenter)
            num_lbl.setObjectName("KeypadNum")
            
            letter_lbl = QLabel(letters)
            letter_lbl.setAlignment(Qt.AlignCenter)
            letter_lbl.setObjectName("KeypadLetters")
            
            key_layout.addWidget(num_lbl)
            key_layout.addWidget(letter_lbl)
            key_widget.setObjectName("KeypadBtn")
            
            grid.addWidget(key_widget, r, c)
            c += 1
            if c > 2:
                c = 0
                r += 1
        
        # Add 0
        zero_widget = QWidget()
        zero_layout = QVBoxLayout(zero_widget)
        zero_layout.setContentsMargins(5, 5, 5, 5)
        zero_num = QLabel("0")
        zero_num.setAlignment(Qt.AlignCenter)
        zero_num.setObjectName("KeypadNum")
        zero_layout.addWidget(zero_num)
        zero_widget.setObjectName("KeypadBtn")
        grid.addWidget(zero_widget, r, 1)

        helper_layout.addLayout(grid)
        
        # Updated Instructions
        instr = QLabel("1. Hold Number to see letters\n2. Move Hand Left/Right\n3. MAKE FIST to Type Letter")
        instr.setAlignment(Qt.AlignCenter)
        instr.setObjectName("HelperText")
        helper_layout.addWidget(instr)
        
        split_layout.addWidget(helper_container, 40)
        content_layout.addLayout(split_layout)
        main_h_layout.addWidget(content_area)

    def apply_styles(self):
        contrast = self.settings.get('high_contrast', False)
        
        base_styles = """
            QWidget#CentralWidget { background-color: #121212; }
            QFrame#Sidebar { background-color: #000000; border-right: 1px solid #333; }
            QLabel#SideBtn { color: #555; font-size: 14px; font-weight: bold; }
            QLabel#SideBtn_Active { color: #00E5FF; font-size: 14px; font-weight: bold; border-left: 4px solid #00E5FF; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1A1A1A, stop:1 #000000); }
            QLabel#StatusBarText { color: #AAA; font-size: 16px; font-weight: 500; }
            QLabel#ConfidenceBar { background-color: #333; border-radius: 4px; }
            QFrame#ListContainer { background-color: #1E1E1E; border-radius: 15px; }
            QLabel#SectionTitle { color: #FFF; font-size: 26px; font-weight: bold; padding-left: 10px; }
            QLabel#InputHUD { background-color: #333; color: #00E5FF; font-size: 18px; font-weight: bold; border-radius: 8px; padding: 8px; border: 1px solid #444; }
            QListWidget#ModernList { background-color: transparent; border: none; outline: none; padding: 10px; }
            QListWidget#ModernList::item { background-color: #252525; color: #DDD; height: 60px; font-size: 22px; margin-bottom: 8px; border-radius: 8px; padding-left: 15px; }
            QListWidget#ModernList::item:selected { background-color: #00E5FF; color: #000; font-weight: bold; }
            QFrame#HelperWidget { background-color: #181818; border-radius: 15px; border: 1px solid #2A2A2A; }
            QLabel#HelperTitle { color: #888; font-size: 14px; letter-spacing: 2px; font-weight: bold; margin-bottom: 10px; }
            
            /* Spatial Zone Styles */
            QLabel#ZoneLabel { 
                background-color: #2A2A2A; color: #555; 
                font-size: 32px; font-weight: bold; 
                border-radius: 10px; margin: 2px;
            }
            
            QWidget#KeypadBtn { background-color: #2A2A2A; border-radius: 10px; min-width: 60px; min-height: 50px; }
            QLabel#KeypadNum { color: #FFF; font-size: 24px; font-weight: bold; }
            QLabel#KeypadLetters { color: #888; font-size: 10px; }
            QLabel#HelperText { color: #666; font-size: 14px; margin-top: 10px; line-height: 140%; }
        """
        
        if contrast:
            base_styles += """
                QWidget#CentralWidget { background-color: #000; }
                QFrame#ListContainer { background-color: #000; border: 2px solid #FFF; }
                QListWidget#ModernList::item { background-color: #111; color: #FFF; }
                QListWidget#ModernList::item:selected { background-color: #FFFF00; color: #000; }
            """
        
        self.setStyleSheet(base_styles)

    def update_clock(self):
        curr_time = time.strftime("%I:%M %p")
        self.clock_label.setText(curr_time)

    def update_confidence_bar(self, confidence):
        color = "#00FF00" if confidence > 0.8 else "#FFAA00" if confidence > 0.6 else "#FF4444"
        self.confidence_bar.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {color}, stop:{confidence} {color}, 
                stop:{confidence} #333, stop:1 #333);
            border-radius: 4px;
        """)

    def check_input_timeout(self):
        # Increased timeout to 8 seconds to give time for spatial selection
        if self.input_buffer and time.time() - self.last_input_time > 8.0:
            self.input_buffer = ""
            self.input_hud.setText("T9: Timeout")
            self.reset_spatial_ui()
            QTimer.singleShot(1000, lambda: self.input_hud.setText("T9: Ready"))

    def handle_digit_input(self, digit_str, confidence):
        self.last_input_time = time.time()
        
        # 1. Handle Backspace (Digit 1)
        if digit_str == '1':
            if self.current_filter:
                self.current_filter = self.current_filter[:-1]
                self.filter_contacts()
                self.input_hud.setText(f"T9: {self.current_filter}_")
                self.reset_spatial_ui()
            return

        # 2. Handle Spatial T9 (Digits 2-9)
        if digit_str in self.T9_MAP:
            # If user switched to a new digit, start tracking
            if digit_str != self.current_digit_held:
                self.current_digit_held = digit_str
                self.spatial_letters = self.T9_MAP[digit_str] # "ABC"
                self.update_spatial_ui() # Show boxes
                
    def handle_spatial_update(self, index):
        """Update highlighted zone based on hand position"""
        if not self.spatial_letters: return
        
        max_idx = len(self.spatial_letters) - 1
        safe_index = min(max(index, 0), max_idx)
        
        if safe_index != self.current_spatial_index:
            self.current_spatial_index = safe_index
            self.update_spatial_ui()

    def handle_spatial_commit(self):
        """Called when Fist (0) is detected - Commits the highlighted letter"""
        if not self.spatial_letters: return
        
        # Get selected char
        idx = min(self.current_spatial_index, len(self.spatial_letters)-1)
        char = self.spatial_letters[idx]
        
        # Add to filter
        self.current_filter += char
        self.filter_contacts()
        self.input_hud.setText(f"Entered: {char}")
        
        if self.settings.get('voice_enabled'):
            self.tts.say(char)
        
        # Visual reset
        self.reset_spatial_ui()
        self.current_digit_held = None

    def update_spatial_ui(self):
        """Redraw the 3 boxes"""
        letters = self.spatial_letters
        
        for i, lbl in enumerate(self.zone_labels):
            # Set Text (A, B, C...)
            if i < len(letters):
                lbl.setText(letters[i])
            else:
                lbl.setText("")
            
            # Set Style (Highlight Active)
            if i == self.current_spatial_index:
                lbl.setStyleSheet("background: #00E5FF; color: #000; font-size: 48px; border: 2px solid #FFF;")
            else:
                lbl.setStyleSheet("background: #2A2A2A; color: #555; font-size: 32px; border: none;")
        
        # Update HUD Preview
        if 0 <= self.current_spatial_index < len(letters):
            char = letters[self.current_spatial_index]
            self.input_hud.setText(f"T9: {self.current_filter}{char}")

    def reset_spatial_ui(self):
        for lbl in self.zone_labels:
            lbl.setStyleSheet("background: #2A2A2A; color: #555; font-size: 32px;")
            lbl.setText("-")
        self.current_spatial_index = 1

    def filter_contacts(self):
        if not self.current_filter:
            self.update_contact_list()
            return
        
        exact_matches = [c for c in self.all_contacts if c.upper().startswith(self.current_filter.upper())]
        fuzzy_matches = difflib.get_close_matches(
            self.current_filter.upper(),
            [c.upper() for c in self.all_contacts],
            n=5, cutoff=0.6
        )
        fuzzy_contacts = [c for c in self.all_contacts if c.upper() in fuzzy_matches]
        all_matches = list(dict.fromkeys(exact_matches + fuzzy_contacts))
        
        self.contact_list.clear()
        if all_matches:
            self.contact_list.addItems(all_matches)
            self.contact_list.setCurrentRow(0)
            self.input_hud.setText(f"T9: {self.current_filter}")
        else:
            self.contact_list.addItem("No matches found")
            self.input_hud.setText(f"T9: {self.current_filter} (0)")

    def update_contact_list(self):
        self.contact_list.clear()
        display_list = []
        for fav in self.favorites:
            if fav in self.all_contacts:
                display_list.append(f"⭐ {fav}")
        recent = sorted(self.call_history.items(), key=lambda x: x[1], reverse=True)[:3]
        for contact, _ in recent:
            if contact not in self.favorites:
                display_list.append(f"🕒 {contact}")
        for contact in self.all_contacts:
            if contact not in self.favorites and contact not in [c for c, _ in recent]:
                display_list.append(contact)
        self.contact_list.addItems(display_list)
        self.contact_list.setCurrentRow(0)

    def handle_scroll(self, direction):
        count = self.contact_list.count()
        if count == 0: return
        curr = self.contact_list.currentRow()
        if curr == -1: curr = 0
        new_row = min(count - 1, curr + 1) if direction == "DOWN" else max(0, curr - 1)
        self.contact_list.setCurrentRow(new_row)
        self.contact_list.scrollToItem(self.contact_list.currentItem())

    def handle_swipe(self, direction):
        if not self.all_contacts: return
        curr_item = self.contact_list.currentItem()
        if not curr_item: return
        curr_name = curr_item.text().lstrip("⭐🕒 ")
        curr_letter = curr_name[0].upper()
        if direction == "RIGHT":
            target_ord = ord(curr_letter) + 1
            if target_ord > ord('Z'): target_ord = ord('A')
        else:
            target_ord = ord(curr_letter) - 1
            if target_ord < ord('A'): target_ord = ord('Z')
        target_letter = chr(target_ord)
        for i in range(self.contact_list.count()):
            name = self.contact_list.item(i).text().lstrip("⭐🕒 ")
            if name[0].upper() == target_letter:
                self.contact_list.setCurrentRow(i)
                self.contact_list.scrollToItem(self.contact_list.item(i))
                if self.settings.get('voice_enabled'):
                    self.tts.say(target_letter)
                break

    def handle_selection(self):
        curr = self.contact_list.currentItem()
        if curr:
            name = curr.text().lstrip("⭐🕒 ")
            self.call_history[name] = time.time()
            self.input_hud.setText(f"📞 CALLING {name.split()[0]}...")
            self.input_hud.setStyleSheet("""
                background-color: #00FF00; color: #000; 
                font-size: 20px; font-weight: bold; 
                border-radius: 8px; padding: 8px;
            """)
            if self.settings.get('voice_enabled'):
                self.tts.say(f"Calling {name}")
            QTimer.singleShot(2000, self.reset_hud_style)

    def handle_disconnect(self):
        self.current_filter = ""
        self.current_t9_letters = ""
        self.input_buffer = ""
        self.update_contact_list()
        self.input_hud.setText("📵 DISCONNECTED")
        self.input_hud.setStyleSheet("""
            background-color: #FF0000; color: #FFF; 
            font-size: 20px; font-weight: bold; 
            border-radius: 8px; padding: 8px;
        """)
        if self.settings.get('voice_enabled'):
            self.tts.say("Call ended")
        QTimer.singleShot(2000, self.reset_hud_style)

    def handle_cancel(self):
        self.current_filter = ""
        self.current_t9_letters = ""
        self.input_buffer = ""
        self.update_contact_list()
        self.input_hud.setText("❌ CANCELLED")
        self.reset_spatial_ui() # Reset zones too
        if self.settings.get('voice_enabled'):
            self.tts.say("Cancelled")
        QTimer.singleShot(1000, lambda: self.input_hud.setText("T9: Ready"))

    def reset_hud_style(self):
        self.input_hud.setText("T9: Ready")
        self.input_hud.setStyleSheet("""
            background-color: #333;
            color: #00E5FF;
            font-size: 18px;
            font-weight: bold;
            border-radius: 8px;
            padding: 8px;
            border: 1px solid #444;
        """)

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_settings = dialog.get_settings()
            self.settings.update(new_settings)
            self.apply_styles()
            self.start_engine()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ModernCarDisplay()
    window.show()
    sys.exit(app.exec_())