"""
Photo button widget for the idle screen.

Large, touch-friendly circular button with icon.
"""

from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QPainter, QColor, QPen, QBrush, QFont


class PhotoButton(QPushButton):
    """
    Large circular photo capture button.
    
    Touch-friendly button with camera icon, shadow effect,
    and press animation.
    """
    
    # Signal emitted when button is clicked
    clicked_signal = pyqtSignal()
    
    def __init__(
        self,
        parent=None,
        size: int = 150,
        color: str = "#e94560",
        hover_color: str = "#ff6b6b",
        pressed_color: str = "#c23a51",
    ):
        super().__init__(parent)
        
        self.button_size = size
        self.base_color = color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self._current_color = color
        self._is_pressed = False
        
        self._setup_button()
        self._setup_effects()
    
    def _setup_button(self):
        """Configure button appearance."""
        # Fixed size circular button
        self.setFixedSize(self.button_size, self.button_size)
        
        # Remove default styling
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        
        # Set tooltip
        self.setToolTip("Foto aufnehmen")
        
        # Apply stylesheet
        self._update_stylesheet()
    
    def _setup_effects(self):
        """Add visual effects."""
        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
    
    def _update_stylesheet(self):
        """Update button stylesheet."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._current_color};
                border: none;
                border-radius: {self.button_size // 2}px;
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.pressed_color};
            }}
        """)
    
    def paintEvent(self, event):
        """Custom paint for camera icon."""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate icon position (centered)
        icon_size = self.button_size // 3
        center_x = self.button_size // 2
        center_y = self.button_size // 2
        
        # Draw camera icon
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Camera body (rounded rectangle)
        body_width = icon_size * 1.4
        body_height = icon_size
        body_x = center_x - body_width / 2
        body_y = center_y - body_height / 2 + 5
        
        painter.drawRoundedRect(
            int(body_x), int(body_y),
            int(body_width), int(body_height),
            8, 8
        )
        
        # Camera lens (circle)
        lens_radius = icon_size // 3
        painter.drawEllipse(
            center_x - lens_radius,
            int(center_y + 5 - lens_radius),
            lens_radius * 2,
            lens_radius * 2
        )
        
        # Camera flash/viewfinder (small rectangle on top)
        flash_width = icon_size // 2
        flash_height = 8
        flash_x = center_x - flash_width / 2
        flash_y = body_y - flash_height + 2
        
        painter.fillRect(
            int(flash_x), int(flash_y),
            int(flash_width), int(flash_height),
            QColor(255, 255, 255)
        )
        
        painter.end()
    
    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self._current_color = self.pressed_color
            self._update_stylesheet()
            
            # Scale down animation
            self.setFixedSize(
                int(self.button_size * 0.95),
                int(self.button_size * 0.95)
            )
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = False
            self._current_color = self.base_color
            self._update_stylesheet()
            
            # Scale back up
            self.setFixedSize(self.button_size, self.button_size)
            
            # Emit signal
            self.clicked_signal.emit()
        
        super().mouseReleaseEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter."""
        if not self._is_pressed:
            self._current_color = self.hover_color
            self._update_stylesheet()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave."""
        if not self._is_pressed:
            self._current_color = self.base_color
            self._update_stylesheet()
        super().leaveEvent(event)
    
    def set_size(self, size: int):
        """Change button size."""
        self.button_size = size
        self.setFixedSize(size, size)
        self._update_stylesheet()
    
    def set_color(self, color: str):
        """Change button base color."""
        self.base_color = color
        self._current_color = color
        self._update_stylesheet()
    
    def sizeHint(self) -> QSize:
        """Suggested widget size."""
        return QSize(self.button_size, self.button_size)
