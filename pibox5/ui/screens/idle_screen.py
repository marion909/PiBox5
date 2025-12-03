"""
Idle screen with blurred preview and photo button.

Main screen shown when waiting for user interaction.
"""

from typing import TYPE_CHECKING

import numpy as np
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont

from pibox5.config import Settings
from pibox5.ui.widgets import LivePreviewWidget, PhotoButton

if TYPE_CHECKING:
    from pibox5.ui.main_window import MainWindow


class IdleScreen(QWidget):
    """
    Idle screen with blurred live preview and photo button.
    
    Features:
    - Full-screen blurred camera preview
    - Large centered photo button
    - Settings button in corner
    """
    
    # Signals
    photo_button_clicked = pyqtSignal()
    settings_button_clicked = pyqtSignal()
    
    def __init__(self, settings: Settings, main_window: "MainWindow"):
        super().__init__()
        
        self.settings = settings
        self.main_window = main_window
        
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
        
        # Live preview (background layer)
        self.preview = LivePreviewWidget(
            self.container,
            blur_radius=self.settings.ui.blur_radius,
        )
        self.preview.blur_enabled = True
        
        # Photo button (foreground layer, centered)
        self.photo_button = PhotoButton(
            self.container,
            size=self.settings.ui.button_size,
        )
        self.photo_button.clicked_signal.connect(self._on_photo_click)
        
        # Settings button (top-right corner) - optimized for 800x480
        self.settings_button = QPushButton("⚙", self.container)
        self.settings_button.setFixedSize(40, 40)
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 20px;
                font-size: 20px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.4);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.6);
            }
        """)
        self.settings_button.clicked.connect(self._on_settings_click)
        
        # Hide settings button if disabled
        if not self.settings.ui.show_settings_button:
            self.settings_button.hide()
        
        # Hint text at bottom
        self.hint_label = QLabel("Tippe den Button für ein Foto", self.container)
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 14px;
                background-color: transparent;
                padding: 5px;
            }
        """)
    
    def resizeEvent(self, event):
        """Handle resize to position widgets."""
        super().resizeEvent(event)
        
        width = self.width()
        height = self.height()
        
        # Make preview fill the entire screen
        self.preview.setGeometry(0, 0, width, height)
        
        # Center photo button
        btn_size = self.photo_button.button_size
        btn_x = (width - btn_size) // 2
        btn_y = (height - btn_size) // 2
        self.photo_button.move(btn_x, btn_y)
        
        # Position settings button in top-right corner
        self.settings_button.move(width - 50, 8)
        
        # Position hint at bottom
        hint_height = 30
        self.hint_label.setGeometry(0, height - hint_height - 10, width, hint_height)
    
    def update_preview(self, frame: np.ndarray, blur: bool = True):
        """
        Update the live preview.
        
        Args:
            frame: BGR numpy array from camera.
            blur: Whether to apply blur effect.
        """
        self.preview.blur_enabled = blur
        self.preview.update_frame(frame)
    
    def _on_photo_click(self):
        """Handle photo button click."""
        self.photo_button_clicked.emit()
    
    def _on_settings_click(self):
        """Handle settings button click."""
        self.settings_button_clicked.emit()
    
    def refresh_settings(self, settings: Settings):
        """Apply new settings."""
        self.settings = settings
        
        # Update blur radius
        self.preview.set_blur_radius(settings.ui.blur_radius)
        
        # Update button size
        self.photo_button.set_size(settings.ui.button_size)
        
        # Update settings button visibility
        self.settings_button.setVisible(settings.ui.show_settings_button)
        
        # Trigger resize to reposition elements
        self.resizeEvent(None)
