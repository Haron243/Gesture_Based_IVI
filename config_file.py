"""
Centralized configuration for Electrifex IVI System
Modify these values to customize system behavior
"""

# ============================================================================
# GESTURE DETECTION SETTINGS
# ============================================================================

class GestureConfig:
    """Gesture recognition parameters"""
    
    # Detection thresholds
    STABILITY_THRESHOLD = 6  # Frames needed for stable gesture (lower = faster, less stable)
    CONFIDENCE_THRESHOLD = 0.70  # Minimum confidence for gesture recognition
    
    # Timing parameters
    COOLDOWN_SECONDS = 0.8  # Time between gesture triggers (prevent double-detection)
    SCROLL_INTERVAL = 0.3  # Time between scroll events
    
    # Gesture thresholds
    PINCH_THRESHOLD = 0.06  # Distance for pinch gesture (thumb-index)
    DISCONNECT_HOLD_TIME = 1.5  # Seconds to hold thumbs-down for disconnect
    CANCEL_HOLD_TIME = 1.0  # Seconds to hold open palm for cancel
    SWIPE_THRESHOLD = 0.2  # Horizontal movement for swipe detection
    
    # Zone definitions (0.0 = top, 1.0 = bottom)
    SCROLL_TOP_ZONE = 0.22  # Upper boundary for scroll-up zone
    SCROLL_BOTTOM_ZONE = 0.78  # Lower boundary for scroll-down zone
    
    # Camera settings
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    CAMERA_INDEX = 0  # 0 = default camera, 1 = external camera
    
    # MediaPipe parameters
    MAX_HANDS = 1  # Track only one hand
    MODEL_COMPLEXITY = 1  # 0=lite, 1=full (balance speed/accuracy)
    MIN_DETECTION_CONFIDENCE = 0.75
    MIN_TRACKING_CONFIDENCE = 0.6
    
    # Performance
    ENABLE_GPU = True  # Use GPU acceleration if available
    FRAME_SKIP = 0  # Skip every N frames (0 = process all)


# ============================================================================
# UI/UX SETTINGS
# ============================================================================

class UIConfig:
    """User interface configuration"""
    
    # Window settings
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    WINDOW_TITLE = "Electrifex IVI System v2.0"
    
    # Theme colors (hex codes)
    class Colors:
        BACKGROUND = "#121212"
        SIDEBAR = "#000000"
        CARD = "#1E1E1E"
        ACCENT = "#00E5FF"
        TEXT_PRIMARY = "#FFFFFF"
        TEXT_SECONDARY = "#AAAAAA"
        SUCCESS = "#00FF00"
        ERROR = "#FF0000"
        WARNING = "#FFAA00"
    
    # Typography
    FONT_FAMILY = "Segoe UI"  # or "Arial", "Roboto", etc.
    FONT_SIZE_LARGE = 26
    FONT_SIZE_MEDIUM = 22
    FONT_SIZE_SMALL = 16
    
    # Layout
    SIDEBAR_WIDTH = 100
    LIST_ITEM_HEIGHT = 60
    ITEM_SPACING = 8
    BORDER_RADIUS = 15
    
    # Animations
    ANIMATION_DURATION_MS = 300
    ENABLE_ANIMATIONS = True
    
    # Input timeout
    INPUT_TIMEOUT_SECONDS = 3.0  # Auto-clear input after inactivity
    T9_COMMIT_DELAY_SECONDS = 1.5  # Auto-commit T9 character


# ============================================================================
# SMART PREDICTION SETTINGS
# ============================================================================

class PredictionConfig:
    """AI contact prediction parameters"""
    
    # Feature weights (must sum to ~1.0)
    WEIGHT_RECENCY = 0.25
    WEIGHT_FREQUENCY = 0.20
    WEIGHT_TIME_PATTERN = 0.20
    WEIGHT_DAY_PATTERN = 0.15
    WEIGHT_LOCATION = 0.10
    WEIGHT_DURATION = 0.10
    
    # Scoring parameters
    FAVORITE_BOOST = 1.5  # Multiply score for favorites
    RECENT_CALL_HOURS = 24  # Hours to consider "recent"
    FREQUENT_CALL_THRESHOLD = 10  # Calls/month for "frequent"
    LONG_CALL_DURATION = 300  # Seconds (5 min) for "long call"
    
    # History management
    MAX_CALL_HISTORY = 100  # Max calls stored per contact
    PATTERN_LOOKBACK_DAYS = 30  # Days of history to analyze
    
    # File storage
    PATTERNS_FILE = "contact_patterns.json"
    AUTO_SAVE = True
    SAVE_INTERVAL_SECONDS = 300  # Save every 5 minutes


# ============================================================================
# VOICE FEEDBACK SETTINGS
# ============================================================================

class VoiceConfig:
    """Text-to-speech configuration"""
    
    ENABLED_BY_DEFAULT = True
    SPEECH_RATE = 0.2  # -1.0 to 1.0 (0 = normal)
    SPEECH_VOLUME = 0.8  # 0.0 to 1.0
    
    # What to announce
    ANNOUNCE_DIGITS = True
    ANNOUNCE_LETTERS = True
    ANNOUNCE_SELECTIONS = True
    ANNOUNCE_ERRORS = False  # Don't announce every error
    
    # Voice prompts
    PROMPTS = {
        'calling': "Calling {name}",
        'call_ended': "Call ended",
        'cancelled': "Cancelled",
        'no_matches': "No contacts found",
        'system_ready': "System ready"
    }


# ============================================================================
# ACCESSIBILITY SETTINGS
# ============================================================================

class AccessibilityConfig:
    """Accessibility and safety features"""
    
    # High contrast mode
    HIGH_CONTRAST_ENABLED = False
    HIGH_CONTRAST_COLORS = {
        'background': '#000000',
        'text': '#FFFFFF',
        'selected': '#FFFF00',
        'border': '#FFFFFF'
    }
    
    # Text scaling
    LARGE_TEXT_MODE = False
    TEXT_SCALE_FACTOR = 1.0  # 1.0 = normal, 1.5 = 150%
    
    # Gesture assistance
    SHOW_HAND_LANDMARKS = True  # Draw skeleton on camera feed
    SHOW_GESTURE_ZONES = True  # Show scroll zone lines
    SHOW_CONFIDENCE_BAR = True
    
    # Safety warnings
    MOTION_WARNING = False  # Warn if vehicle is moving (requires GPS)
    ATTENTION_TIMEOUT = 10  # Seconds of inactivity before auto-dismiss


# ============================================================================
# DEVELOPMENT & DEBUG SETTINGS
# ============================================================================

class DebugConfig:
    """Development and debugging options"""
    
    # Logging
    ENABLE_LOGGING = True
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
    LOG_FILE = "electrifex_ivi.log"
    
    # Debug windows
    SHOW_CAMERA_FEED = True  # Show gesture detection window
    SHOW_FPS = True  # Display frame rate
    SHOW_LATENCY = True  # Display detection latency
    
    # Performance monitoring
    COLLECT_METRICS = True
    METRICS_FILE = "performance_metrics.json"
    
    # Testing
    DEMO_MODE = False  # Use fake contacts and simulated calls
    SKIP_CAMERA_CHECK = False  # Start even if no camera found
    
    # Advanced
    PROFILE_PERFORMANCE = False  # Detailed profiling (impacts speed)
    SAVE_FAILED_FRAMES = False  # Save frames where detection failed


# ============================================================================
# HARDWARE INTEGRATION SETTINGS
# ============================================================================

class HardwareConfig:
    """Integration with vehicle hardware"""
    
    # CAN bus integration (future)
    CAN_ENABLED = False
    CAN_INTERFACE = "can0"
    
    # GPS integration
    GPS_ENABLED = False
    GPS_PORT = "/dev/ttyUSB0"
    
    # Display
    FULLSCREEN = False
    HIDE_CURSOR = False  # Hide mouse cursor in production
    
    # Input devices
    TOUCH_ENABLED = True  # Allow touch as fallback
    STEERING_WHEEL_BUTTONS = False  # Use wheel buttons for navigation


# ============================================================================
# VALIDATION & SANITY CHECKS
# ============================================================================

def validate_config():
    """Validate configuration values"""
    errors = []
    
    # Check weights sum
    weights_sum = sum([
        PredictionConfig.WEIGHT_RECENCY,
        PredictionConfig.WEIGHT_FREQUENCY,
        PredictionConfig.WEIGHT_TIME_PATTERN,
        PredictionConfig.WEIGHT_DAY_PATTERN,
        PredictionConfig.WEIGHT_LOCATION,
        PredictionConfig.WEIGHT_DURATION
    ])
    
    if not 0.95 <= weights_sum <= 1.05:
        errors.append(f"Prediction weights sum to {weights_sum}, should be ~1.0")
    
    # Check zone boundaries
    if GestureConfig.SCROLL_TOP_ZONE >= GestureConfig.SCROLL_BOTTOM_ZONE:
        errors.append("SCROLL_TOP_ZONE must be less than SCROLL_BOTTOM_ZONE")
    
    # Check thresholds
    if GestureConfig.CONFIDENCE_THRESHOLD < 0.5:
        errors.append("CONFIDENCE_THRESHOLD too low, may cause false positives")
    
    if errors:
        print("⚠️  Configuration Issues Found:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Configuration validated successfully")
    return True


# ============================================================================
# PRESET CONFIGURATIONS
# ============================================================================

class Presets:
    """Pre-configured settings for different scenarios"""
    
    @staticmethod
    def apply_performance_mode():
        """Optimize for speed over accuracy"""
        GestureConfig.STABILITY_THRESHOLD = 4
        GestureConfig.MODEL_COMPLEXITY = 0
        GestureConfig.FRAME_SKIP = 1
        UIConfig.ENABLE_ANIMATIONS = False
        print("⚡ Performance mode activated")
    
    @staticmethod
    def apply_accuracy_mode():
        """Optimize for accuracy over speed"""
        GestureConfig.STABILITY_THRESHOLD = 8
        GestureConfig.CONFIDENCE_THRESHOLD = 0.85
        GestureConfig.MODEL_COMPLEXITY = 1
        print("🎯 Accuracy mode activated")
    
    @staticmethod
    def apply_debug_mode():
        """Enable all debugging features"""
        DebugConfig.ENABLE_LOGGING = True
        DebugConfig.LOG_LEVEL = "DEBUG"
        DebugConfig.SHOW_CAMERA_FEED = True
        DebugConfig.SHOW_FPS = True
        DebugConfig.COLLECT_METRICS = True
        AccessibilityConfig.SHOW_HAND_LANDMARKS = True
        AccessibilityConfig.SHOW_GESTURE_ZONES = True
        print("🐛 Debug mode activated")
    
    @staticmethod
    def apply_production_mode():
        """Production-ready settings"""
        DebugConfig.SHOW_CAMERA_FEED = False
        DebugConfig.COLLECT_METRICS = False
        HardwareConfig.FULLSCREEN = True
        HardwareConfig.HIDE_CURSOR = True
        print("🚀 Production mode activated")
    
    @staticmethod
    def apply_accessibility_mode():
        """Enhanced accessibility features"""
        VoiceConfig.ENABLED_BY_DEFAULT = True
        VoiceConfig.ANNOUNCE_DIGITS = True
        VoiceConfig.ANNOUNCE_LETTERS = True
        AccessibilityConfig.HIGH_CONTRAST_ENABLED = True
        AccessibilityConfig.LARGE_TEXT_MODE = True
        AccessibilityConfig.TEXT_SCALE_FACTOR = 1.3
        print("♿ Accessibility mode activated")


# ============================================================================
# EXPORT ALL CONFIGS
# ============================================================================

def export_config_dict():
    """Export all config as dictionary"""
    return {
        'gesture': {k: v for k, v in vars(GestureConfig).items() if not k.startswith('_')},
        'ui': {k: v for k, v in vars(UIConfig).items() if not k.startswith('_')},
        'prediction': {k: v for k, v in vars(PredictionConfig).items() if not k.startswith('_')},
        'voice': {k: v for k, v in vars(VoiceConfig).items() if not k.startswith('_')},
        'accessibility': {k: v for k, v in vars(AccessibilityConfig).items() if not k.startswith('_')},
        'debug': {k: v for k, v in vars(DebugConfig).items() if not k.startswith('_')},
        'hardware': {k: v for k, v in vars(HardwareConfig).items() if not k.startswith('_')}
    }


# Run validation when module is imported
if __name__ == "__main__":
    print("\n" + "="*60)
    print("ELECTRIFEX IVI SYSTEM - CONFIGURATION")
    print("="*60 + "\n")
    validate_config()
    print("\nAvailable presets:")
    print("  - Presets.apply_performance_mode()")
    print("  - Presets.apply_accuracy_mode()")
    print("  - Presets.apply_debug_mode()")
    print("  - Presets.apply_production_mode()")
    print("  - Presets.apply_accessibility_mode()")
