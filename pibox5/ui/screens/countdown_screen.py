"""
Countdown screen with clear preview and animated timer.

Shown after photo button is pressed, before capture.
"""

from typing import TYPE_CHECKING

import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont

from pibox5.config import Settings
from pibox5.ui.widgets import LivePreviewWidget

if TYPE_CHECKING:
    from pibox5.ui.main_window import MainWindow


class CountdownScreen(QWidget):
    """
    Countdown screen with clear live preview and animated countdown.
    
    Features:
    - Full-screen clear (non-blurred) camera preview
    - Large animated countdown numbers
    - Configurable countdown duration
    """
    
    # Signal emitted when countdown reaches 0
    countdown_finished = pyqtSignal()
    
    def __init__(self, settings: Settings, main_window: "MainWindow"):
        super().__init__()
        
        self.settings = settings
        self.main_window = main_window
        
        self._countdown_value = 0
        self._timer: QTimer = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Container for layered widgets
        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.container)
        
        # Live preview (background layer) - no blur
        self.preview = LivePreviewWidget(self.container)
        self.preview.blur_enabled = False
        
        # Countdown label (centered overlay)
        self.countdown_label = QLabel("", self.container)
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_countdown_style()
        
        # "Get ready" hint at top
        self.hint_label = QLabel("Bereit machen!", self.container)
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 28px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0.5);
                padding: 15px 30px;
                border-radius: 10px;
            }
        """)
        
        # Create timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
    
    def _update_countdown_style(self):
        """Update countdown label style."""
        font_size = self.settings.ui.countdown_font_size
        self.countdown_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: {font_size}px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0.5);
                border-radius: 20px;
                padding: 20px 40px;
            }}
        """)
    
    def resizeEvent(self, event):
        """Handle resize to position widgets."""
        super().resizeEvent(event)
        
        width = self.width()
        height = self.height()
        
        # Make preview fill the entire screen
        self.preview.setGeometry(0, 0, width, height)
        
        # Center countdown label
        label_width = 200
        label_height = 200
        label_x = (width - label_width) // 2
        label_y = (height - label_height) // 2
        self.countdown_label.setGeometry(label_x, label_y, label_width, label_height)
        
        # Position hint at top center
        hint_width = 300
        hint_height = 60
        hint_x = (width - hint_width) // 2
        self.hint_label.setGeometry(hint_x, 30, hint_width, hint_height)
    
    def update_preview(self, frame: np.ndarray, blur: bool = False):
        """
        Update the live preview.
        
        Args:
            frame: BGR numpy array from camera.
            blur: Whether to apply blur (always False for countdown).
        """
        self.preview.blur_enabled = False  # Never blur during countdown
        self.preview.update_frame(frame)
    
    def start_countdown(self):
        """Start the countdown timer."""
        self._countdown_value = self.settings.timing.countdown_seconds
        self.countdown_label.setText(str(self._countdown_value))
        self.countdown_label.show()
        self.hint_label.show()
        
        # Animate the first number
        self._animate_number()
        
        # Start timer (1 second intervals)
        self._timer.start(1000)
    
    def stop_countdown(self):
        """Stop the countdown timer."""
        self._timer.stop()
        self.countdown_label.hide()
        self.hint_label.hide()
    
    def _tick(self):
        """Handle timer tick."""
        self._countdown_value -= 1
        
        if self._countdown_value <= 0:
            # Countdown finished
            self._timer.stop()
            self.countdown_label.setText("📸")
            self._animate_number()
            
            # Delay slightly before capture to show flash icon
            QTimer.singleShot(300, self._finish_countdown)
        else:
            # Update display
            self.countdown_label.setText(str(self._countdown_value))
            self._animate_number()
            
            # Change hint text for last seconds
            if self._countdown_value == 1:
                self.hint_label.setText("Lächeln!")
    
    def _animate_number(self):
        """Animate the countdown number."""
        # Simple scale animation effect using stylesheet
        font_size = self.settings.ui.countdown_font_size
        
        # Start larger and animate to normal size
        large_size = int(font_size * 1.3)
        
        self.countdown_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: {large_size}px;
                font-weight: bold;
                background-color: rgba(233, 69, 96, 0.8);
                border-radius: 20px;
                padding: 20px 40px;
            }}
        """)
        
        # After short delay, return to normal size
        QTimer.singleShot(200, lambda: self.countdown_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: {font_size}px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0.5);
                border-radius: 20px;
                padding: 20px 40px;
            }}
        """))
    
    def _finish_countdown(self):
        """Handle countdown completion."""
        self.countdown_label.hide()
        self.hint_label.hide()
        self.countdown_finished.emit()
    
    def refresh_settings(self, settings: Settings):
        """Apply new settings."""
        self.settings = settings
        self._update_countdown_style()
