"""
Review screen for displaying captured photo.

Shows photo with auto-timeout and upload status.
"""

from typing import TYPE_CHECKING, Optional
from io import BytesIO

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage

from pibox5.config import Settings

if TYPE_CHECKING:
    from pibox5.ui.main_window import MainWindow


class ReviewScreen(QWidget):
    """
    Review screen for displaying captured photos.
    
    Features:
    - Full-screen photo display
    - Progress bar showing remaining review time
    - Auto-return to idle after configurable timeout
    """
    
    # Signal emitted when review period ends
    review_finished = pyqtSignal()
    
    def __init__(self, settings: Settings, main_window: "MainWindow"):
        super().__init__()
        
        self.settings = settings
        self.main_window = main_window
        
        self._review_timer: QTimer = None
        self._progress_timer: QTimer = None
        self._remaining_seconds = 0
        self._total_seconds = 0
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Container
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #1a1a2e;")
        layout.addWidget(self.container)
        
        # Photo display
        self.photo_label = QLabel(self.container)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setStyleSheet("background-color: #1a1a2e;")
        
        # Success message overlay
        self.message_label = QLabel("✓ Foto aufgenommen!", self.container)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
                background-color: rgba(46, 204, 113, 0.9);
                padding: 12px 25px;
                border-radius: 10px;
            }
        """)
        
        # Progress bar at bottom
        self.progress_bar = QProgressBar(self.container)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.2);
                border: none;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #e94560;
            }
        """)
        
        # Timer label
        self.timer_label = QLabel("", self.container)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 16px;
                background-color: transparent;
            }
        """)
        
        # Create timers
        self._review_timer = QTimer(self)
        self._review_timer.setSingleShot(True)
        self._review_timer.timeout.connect(self._on_review_timeout)
        
        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._update_progress)
    
    def resizeEvent(self, event):
        """Handle resize to position widgets."""
        super().resizeEvent(event)
        
        width = self.width()
        height = self.height()
        
        # Photo fills most of the screen
        photo_margin = 20
        photo_bottom_margin = 80  # Leave space for progress bar
        self.photo_label.setGeometry(
            photo_margin,
            photo_margin,
            width - 2 * photo_margin,
            height - photo_margin - photo_bottom_margin,
        )
        
        # Message at top center
        msg_width = 400
        msg_height = 80
        msg_x = (width - msg_width) // 2
        self.message_label.setGeometry(msg_x, 30, msg_width, msg_height)
        
        # Progress bar at bottom
        bar_height = 8
        bar_margin = 30
        self.progress_bar.setGeometry(
            bar_margin,
            height - 50,
            width - 2 * bar_margin,
            bar_height,
        )
        
        # Timer label below message
        self.timer_label.setGeometry(0, height - 35, width, 25)
        
        # Re-scale photo if we have one
        if hasattr(self, '_current_pixmap') and self._current_pixmap:
            self._display_scaled_pixmap()
    
    def set_photo(self, image_data: bytes):
        """
        Set the photo to display.
        
        Args:
            image_data: JPEG image data bytes.
        """
        # Load image from bytes
        q_image = QImage()
        q_image.loadFromData(image_data)
        
        # Convert to pixmap
        self._current_pixmap = QPixmap.fromImage(q_image)
        self._display_scaled_pixmap()
    
    def _display_scaled_pixmap(self):
        """Scale and display the current pixmap."""
        if not hasattr(self, '_current_pixmap') or not self._current_pixmap:
            return
        
        # Scale to fit label while maintaining aspect ratio
        scaled = self._current_pixmap.scaled(
            self.photo_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.photo_label.setPixmap(scaled)
    
    def start_review_timer(self):
        """Start the review countdown."""
        self._total_seconds = self.settings.timing.review_seconds
        self._remaining_seconds = self._total_seconds
        
        # Update UI
        self.message_label.show()
        self.progress_bar.setMaximum(self._total_seconds * 10)  # 10 steps per second
        self.progress_bar.setValue(self._total_seconds * 10)
        self._update_timer_label()
        
        # Start timers
        self._review_timer.start(self._total_seconds * 1000)
        self._progress_timer.start(100)  # Update every 100ms
        
        # Hide message after 2 seconds
        QTimer.singleShot(2000, self.message_label.hide)
    
    def stop_review_timer(self):
        """Stop the review countdown."""
        self._review_timer.stop()
        self._progress_timer.stop()
    
    def _update_progress(self):
        """Update progress bar and timer."""
        current_value = self.progress_bar.value()
        if current_value > 0:
            self.progress_bar.setValue(current_value - 1)
            
            # Update remaining seconds
            self._remaining_seconds = current_value // 10
            self._update_timer_label()
    
    def _update_timer_label(self):
        """Update the timer display."""
        self.timer_label.setText(
            f"Weiter in {self._remaining_seconds} Sekunden..."
        )
    
    def _on_review_timeout(self):
        """Handle review timer completion."""
        self._progress_timer.stop()
        self.progress_bar.setValue(0)
        self.review_finished.emit()
    
    def refresh_settings(self, settings: Settings):
        """Apply new settings."""
        self.settings = settings
