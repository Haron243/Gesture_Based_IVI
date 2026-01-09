import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QLabel, QFrame, QGridLayout, 
                             QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QColor, QIcon
import time
from gesture_thread import GestureThread

class ModernCarDisplay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Electrifex IVI System")
        self.setGeometry(100, 100, 1280, 720) # 720p HD resolution
        
        # --- DATA ---
        self.all_contacts = [
            "Aaron Smith", "Adam Driver", "Ben Affleck", "Brian O'Conner", 
            "Charlie Puth", "Chris Evans", "Daniel Craig", "David Beckham", 
            "Electrifex Support", "Elon Musk", "Frank Ocean", "George Clooney",
            "Harry Styles", "Henry Cavill", "Ian Somerhalder", "Jack Sparrow", 
            "Jason Statham", "Kevin Hart", "Liam Neeson", "Luke Skywalker",
            "Zendaya", "Zac Efron"
        ]
        
        self.input_buffer = "" 
        self.last_input_time = time.time()
        
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
        self.thread = GestureThread()
        self.thread.gesture_detected.connect(self.handle_digit_input)
        self.thread.scroll_detected.connect(self.handle_scroll)
        self.thread.select_detected.connect(self.handle_selection)
        self.thread.disconnect_detected.connect(self.handle_disconnect)
        self.thread.start()

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    def init_ui(self):
        # MAIN CONTAINER (Dark Background)
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        
        # Main Horizontal Layout (Sidebar | Content)
        main_h_layout = QHBoxLayout(central_widget)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(0)

        # --- 1. SIDEBAR (Global Navigation) ---
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(100)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 30, 0, 30)
        side_layout.setSpacing(40)

        # Fake Icons (Using Text for simplicity, but designed like icons)
        for icon_text, active in [("NAV", False), ("MEDIA", False), ("PHONE", True), ("SET", False)]:
            btn = QLabel(icon_text)
            btn.setAlignment(Qt.AlignCenter)
            btn.setObjectName("SideBtn_Active" if active else "SideBtn")
            btn.setFixedHeight(60)
            side_layout.addWidget(btn)
        
        side_layout.addStretch()
        main_h_layout.addWidget(sidebar)

        # --- 2. MAIN CONTENT AREA ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 20, 30, 20)
        
        # A. STATUS BAR (Top)
        status_bar = QHBoxLayout()
        self.clock_label = QLabel("12:00 PM")
        self.clock_label.setObjectName("StatusBarText")
        temp_label = QLabel("24°C  |  5G")
        temp_label.setObjectName("StatusBarText")
        status_bar.addWidget(self.clock_label)
        status_bar.addStretch()
        status_bar.addWidget(temp_label)
        content_layout.addLayout(status_bar)

        # B. DYNAMIC CONTENT SPLIT (List | HUD)
        split_layout = QHBoxLayout()
        split_layout.setSpacing(30)
        
        # LEFT: Contact List Container
        list_container = QFrame()
        list_container.setObjectName("ListContainer")
        list_layout = QVBoxLayout(list_container)
        
        # Header with Input Overlay
        header_row = QHBoxLayout()
        lbl_title = QLabel("Recent Contacts")
        lbl_title.setObjectName("SectionTitle")
        
        self.input_hud = QLabel("GESTURE: _")
        self.input_hud.setObjectName("InputHUD")
        self.input_hud.setAlignment(Qt.AlignCenter)
        self.input_hud.setFixedWidth(180)
        
        header_row.addWidget(lbl_title)
        header_row.addStretch()
        header_row.addWidget(self.input_hud)
        list_layout.addLayout(header_row)

        # The Actual List
        self.contact_list = QListWidget()
        self.contact_list.setObjectName("ModernList")
        self.contact_list.addItems(self.all_contacts)
        self.contact_list.setCurrentRow(0) # Highlight first by default
        list_layout.addWidget(self.contact_list)
        
        split_layout.addWidget(list_container, 65) # 65% width

        # RIGHT: Gesture Helper (The "Widget" View)
        helper_container = QFrame()
        helper_container.setObjectName("HelperWidget")
        helper_layout = QVBoxLayout(helper_container)
        helper_layout.setContentsMargins(20, 20, 20, 20)
        
        helper_title = QLabel("GESTURE MAP")
        helper_title.setAlignment(Qt.AlignCenter)
        helper_title.setObjectName("HelperTitle")
        helper_layout.addWidget(helper_title)

        # Gesture Grid
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Create visual keypad
        key_map = [
            ('1', 'A'), ('2', 'B'), ('3', 'C'),
            ('4', 'D'), ('5', 'E'), ('6', 'F'),
            ('7', 'G'), ('8', 'H'), ('9', 'I')
        ] # Just visual filler, logic is 01-26
        
        # We will make a simpler 1-9 grid for visualization
        r, c = 0, 0
        for i in range(1, 10):
            k = QLabel(str(i))
            k.setAlignment(Qt.AlignCenter)
            k.setObjectName("KeypadBtn")
            grid.addWidget(k, r, c)
            c += 1
            if c > 2:
                c = 0
                r += 1
        
        # Add '0'
        zero_k = QLabel("0")
        zero_k.setAlignment(Qt.AlignCenter)
        zero_k.setObjectName("KeypadBtn")
        grid.addWidget(zero_k, r, 1)

        helper_layout.addLayout(grid)
        
        # Instructions
        instr = QLabel("0 + 1  =  A\n0 + 2  =  B\n...\n2 + 6  =  Z")
        instr.setAlignment(Qt.AlignCenter)
        instr.setObjectName("HelperText")
        helper_layout.addWidget(instr)
        
        split_layout.addWidget(helper_container, 35) # 35% width

        content_layout.addLayout(split_layout)
        main_h_layout.addWidget(content_area)

    def apply_styles(self):
        # AUTOMOTIVE DARK THEME (CSS)
        self.setStyleSheet("""
            QWidget#CentralWidget {
                background-color: #121212;
            }
            /* SIDEBAR */
            QFrame#Sidebar {
                background-color: #000000;
                border-right: 1px solid #333;
            }
            QLabel#SideBtn {
                color: #555;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
            QLabel#SideBtn_Active {
                color: #00E5FF;
                font-size: 14px;
                font-weight: bold;
                border-left: 4px solid #00E5FF;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1A1A1A, stop:1 #000000);
            }

            /* STATUS BAR */
            QLabel#StatusBarText {
                color: #AAA;
                font-size: 16px;
                font-weight: 500;
            }

            /* LIST CONTAINER */
            QFrame#ListContainer {
                background-color: #1E1E1E;
                border-radius: 15px;
            }
            QLabel#SectionTitle {
                color: #FFF;
                font-size: 26px;
                font-weight: bold;
                padding-left: 10px;
            }
            QLabel#InputHUD {
                background-color: #333;
                color: #00E5FF;
                font-size: 20px;
                font-weight: bold;
                border-radius: 8px;
                padding: 5px;
                border: 1px solid #444;
            }

            /* MODERN LIST WIDGET */
            QListWidget#ModernList {
                background-color: transparent;
                border: none;
                outline: none;
                padding: 10px;
            }
            QListWidget#ModernList::item {
                background-color: #252525;
                color: #DDD;
                height: 60px; /* Taller Rows for Cars */
                font-size: 22px;
                margin-bottom: 8px; /* Spacing between cards */
                border-radius: 8px;
                padding-left: 15px;
            }
            QListWidget#ModernList::item:selected {
                background-color: #00E5FF;
                color: #000;
                font-weight: bold;
            }

            /* RIGHT PANEL (WIDGET) */
            QFrame#HelperWidget {
                background-color: #181818;
                border-radius: 15px;
                border: 1px solid #2A2A2A;
            }
            QLabel#HelperTitle {
                color: #888;
                font-size: 14px;
                letter-spacing: 2px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QLabel#KeypadBtn {
                background-color: #2A2A2A;
                color: #FFF;
                font-size: 24px;
                font-weight: bold;
                border-radius: 10px;
                min-width: 60px;
                min-height: 50px;
            }
            QLabel#HelperText {
                color: #666;
                font-size: 16px;
                margin-top: 15px;
                line-height: 140%;
            }
        """)

    # --- LOGIC METHODS ---
    def update_clock(self):
        curr_time = time.strftime("%I:%M %p")
        self.clock_label.setText(curr_time)

    def check_input_timeout(self):
        # Auto-clear input if idle for 2 seconds
        if self.input_buffer and time.time() - self.last_input_time > 2.0:
            self.input_buffer = ""
            self.input_hud.setText("GESTURE: _")

    def handle_digit_input(self, digit_str):
        self.last_input_time = time.time()
        self.input_buffer += digit_str
        self.input_hud.setText(f"GESTURE: {self.input_buffer}")
        
        # Flash the keypad button visually (optional polish)
        # Check if buffer is full (2 digits)
        if len(self.input_buffer) >= 2:
            try:
                val = int(self.input_buffer)
                if 1 <= val <= 26:
                    char = chr(val + 64)
                    self.filter_list_by_char(char)
                else:
                    self.input_hud.setText("INVALID")
            except:
                pass
            # Clear buffer logic handled by next input or timeout
            self.input_buffer = "" # Reset immediately for next char

    def filter_list_by_char(self, char):
        self.input_hud.setText(f"FILTER: {char}")
        
        # Find matches
        matches = [c for c in self.all_contacts if c.upper().startswith(char)]
        
        self.contact_list.clear()
        if matches:
            self.contact_list.addItems(matches)
            self.contact_list.setCurrentRow(0)
        else:
            item = "No Contacts Found"
            self.contact_list.addItem(item)

    def handle_scroll(self, direction):
        count = self.contact_list.count()
        if count == 0: return
        
        curr = self.contact_list.currentRow()
        if curr == -1: curr = 0
        
        if direction == "DOWN":
            new_row = min(count - 1, curr + 1)
        elif direction == "UP":
            new_row = max(0, curr - 1)
        else:
            return
            
        self.contact_list.setCurrentRow(new_row)
        # Smooth scroll feel
        self.contact_list.scrollToItem(self.contact_list.currentItem())

    def handle_selection(self):
        curr = self.contact_list.currentItem()
        if curr:
            name = curr.text()
            self.input_hud.setText(f"CALLING...")
            self.input_hud.setStyleSheet("background-color: #00FF00; color: #000; border: none; font-size: 20px; font-weight: bold; border-radius: 8px;")
            
            # Flash Green
            QTimer.singleShot(1500, self.reset_hud_style)

    def handle_disconnect(self):
        self.input_buffer = ""
        self.contact_list.clear()
        self.contact_list.addItems(self.all_contacts)
        self.contact_list.setCurrentRow(0)
        
        self.input_hud.setText("DISCONNECTED")
        self.input_hud.setStyleSheet("background-color: #FF0000; color: #FFF; border: none; font-size: 20px; font-weight: bold; border-radius: 8px;")
        
        QTimer.singleShot(1500, self.reset_hud_style)

    def reset_hud_style(self):
        self.input_hud.setText("GESTURE: _")
        self.input_hud.setStyleSheet("""
            background-color: #333;
            color: #00E5FF;
            font-size: 20px;
            font-weight: bold;
            border-radius: 8px;
            padding: 5px;
            border: 1px solid #444;
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernCarDisplay()
    window.show()
    sys.exit(app.exec_())