"""
Live preview widget with optional blur effect.

Displays camera preview frames with configurable blur.
"""

from typing import Optional

import numpy as np
import cv2
from PyQt6.QtWidgets import QLabel, QGraphicsBlurEffect
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QImage, QPixmap


class LivePreviewWidget(QLabel):
    """
    Widget for displaying live camera preview.
    
    Supports both blurred and clear preview modes with
    efficient frame conversion and scaling.
    """
    
    def __init__(
        self,
        parent=None,
        blur_radius: int = 20,
        maintain_aspect: bool = True,
    ):
        super().__init__(parent)
        
        self.blur_radius = blur_radius
        self.maintain_aspect = maintain_aspect
        self._blur_enabled = False
        self._current_frame: Optional[np.ndarray] = None
        
        # Setup widget
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(320, 240)
        self.setStyleSheet("background-color: #000;")
        
        # Create blur effect (disabled by default)
        self._blur_effect = QGraphicsBlurEffect()
        self._blur_effect.setBlurRadius(blur_radius)
        self._blur_effect.setEnabled(False)
        self.setGraphicsEffect(self._blur_effect)
    
    @property
    def blur_enabled(self) -> bool:
        """Check if blur effect is enabled."""
        return self._blur_enabled
    
    @blur_enabled.setter
    def blur_enabled(self, enabled: bool):
        """Enable or disable blur effect."""
        self._blur_enabled = enabled
        self._blur_effect.setEnabled(enabled)
    
    def set_blur_radius(self, radius: int):
        """Set the blur effect radius."""
        self.blur_radius = radius
        self._blur_effect.setBlurRadius(radius)
    
    def update_frame(self, frame: np.ndarray, apply_blur: bool = False):
        """
        Update the preview with a new frame.
        
        Args:
            frame: BGR numpy array from camera.
            apply_blur: Whether to apply software blur (alternative to Qt effect).
        """
        if frame is None:
            return
        
        self._current_frame = frame
        
        # Apply software blur if requested (for better performance on slow hardware)
        if apply_blur and not self._blur_enabled:
            # Use OpenCV Gaussian blur for software blurring
            frame = cv2.GaussianBlur(frame, (31, 31), 0)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Get frame dimensions
        height, width, channels = rgb_frame.shape
        bytes_per_line = channels * width
        
        # Create QImage from numpy array
        q_image = QImage(
            rgb_frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888,
        )
        
        # Convert to pixmap and scale
        pixmap = QPixmap.fromImage(q_image)
        
        if self.maintain_aspect:
            # Scale to fit widget while maintaining aspect ratio
            scaled = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        else:
            # Scale to fill widget
            scaled = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        
        self.setPixmap(scaled)
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get the current frame (for capture purposes)."""
        return self._current_frame
    
    def clear_preview(self):
        """Clear the preview display."""
        self.clear()
        self._current_frame = None
    
    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
        
        # Re-render current frame at new size if available
        if self._current_frame is not None:
            self.update_frame(self._current_frame)
    
    def sizeHint(self) -> QSize:
        """Suggested widget size."""
        return QSize(800, 480)
