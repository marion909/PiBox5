"""
Main window for PiBox5 Photo Booth.

Contains the screen navigation and camera management.
"""

from typing import Optional
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QWidget,
    QVBoxLayout,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap

from pibox5.config import Settings, save_settings, ensure_photos_dir
from pibox5.camera import CameraBase, DummyCamera
from pibox5.upload import HttpUploader

# Conditional import for gphoto2
try:
    from pibox5.camera import GPhoto2Camera
except ImportError:
    GPhoto2Camera = None


class CameraThread(QThread):
    """Background thread for camera preview capture."""
    
    frame_ready = pyqtSignal(object)  # Emits numpy array
    
    def __init__(self, camera: CameraBase, fps: int = 10):
        super().__init__()
        self.camera = camera
        self.fps = fps
        self._running = False
    
    def run(self):
        """Capture preview frames in a loop."""
        self._running = True
        interval_ms = 1000 // self.fps
        
        while self._running:
            frame = self.camera.get_preview_frame()
            if frame is not None:
                self.frame_ready.emit(frame)
            self.msleep(interval_ms)
    
    def stop(self):
        """Stop the preview thread."""
        self._running = False
        self.wait()


class MainWindow(QMainWindow):
    """
    Main application window.
    
    Manages screen navigation, camera, and application state.
    """
    
    # Screen indices
    SCREEN_IDLE = 0
    SCREEN_COUNTDOWN = 1
    SCREEN_REVIEW = 2
    SCREEN_SETTINGS = 3
    
    def __init__(self, settings: Settings):
        super().__init__()
        
        self.settings = settings
        self.camera: Optional[CameraBase] = None
        self.camera_thread: Optional[CameraThread] = None
        self.uploader: Optional[HttpUploader] = None
        self.last_photo_data: Optional[bytes] = None
        
        self._setup_ui()
        self._setup_camera()
        self._setup_uploader()
    
    def _setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PiBox5 Photo Booth")
        self.setStyleSheet("background-color: #1a1a2e;")
        
        # Remove window decorations for kiosk mode
        if self.settings.ui.fullscreen:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint
            )
        
        # Enable touch
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        
        # Central widget with stacked screens
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Stacked widget for screen navigation
        self.screen_stack = QStackedWidget()
        layout.addWidget(self.screen_stack)
        
        # Import and create screens
        from pibox5.ui.screens import (
            IdleScreen,
            CountdownScreen,
            ReviewScreen,
            SettingsScreen,
        )
        
        # Create screens
        self.idle_screen = IdleScreen(self.settings, self)
        self.countdown_screen = CountdownScreen(self.settings, self)
        self.review_screen = ReviewScreen(self.settings, self)
        self.settings_screen = SettingsScreen(self.settings, self)
        
        # Add screens to stack
        self.screen_stack.addWidget(self.idle_screen)      # Index 0
        self.screen_stack.addWidget(self.countdown_screen)  # Index 1
        self.screen_stack.addWidget(self.review_screen)     # Index 2
        self.screen_stack.addWidget(self.settings_screen)   # Index 3
        
        # Connect signals
        self.idle_screen.photo_button_clicked.connect(self._on_photo_button)
        self.idle_screen.settings_button_clicked.connect(self._on_settings_button)
        self.countdown_screen.countdown_finished.connect(self._on_countdown_finished)
        self.review_screen.review_finished.connect(self._on_review_finished)
        self.settings_screen.settings_closed.connect(self._on_settings_closed)
        self.settings_screen.settings_saved.connect(self._on_settings_saved)
        
        # Start on idle screen
        self.screen_stack.setCurrentIndex(self.SCREEN_IDLE)
    
    def _setup_camera(self):
        """Initialize the camera."""
        try:
            if self.settings.camera.use_dummy or GPhoto2Camera is None:
                print("[MainWindow] Using dummy camera")
                self.camera = DummyCamera()
            else:
                print("[MainWindow] Using gPhoto2 camera")
                self.camera = GPhoto2Camera()
            
            # Connect to camera
            if self.camera.connect():
                # Start preview thread
                self.camera_thread = CameraThread(
                    self.camera,
                    self.settings.camera.preview_fps
                )
                self.camera_thread.frame_ready.connect(self._on_preview_frame)
                self.camera_thread.start()
                print("[MainWindow] Camera preview started")
            else:
                print("[MainWindow] Failed to connect to camera")
                
        except Exception as e:
            print(f"[MainWindow] Camera setup error: {e}")
            # Fall back to dummy camera
            self.camera = DummyCamera()
            self.camera.connect()
            self.camera_thread = CameraThread(self.camera, 10)
            self.camera_thread.frame_ready.connect(self._on_preview_frame)
            self.camera_thread.start()
    
    def _setup_uploader(self):
        """Initialize the HTTP uploader."""
        if self.settings.upload.enabled and self.settings.upload.url:
            self.uploader = HttpUploader(
                url=self.settings.upload.url,
                api_key=self.settings.upload.api_key,
                timeout=self.settings.upload.timeout_seconds,
                retry_count=self.settings.upload.retry_count,
            )
            print(f"[MainWindow] Uploader configured: {self.settings.upload.url}")
        else:
            self.uploader = None
    
    def _on_preview_frame(self, frame):
        """Handle new preview frame from camera."""
        current_screen = self.screen_stack.currentIndex()
        
        if current_screen == self.SCREEN_IDLE:
            self.idle_screen.update_preview(frame, blur=True)
        elif current_screen == self.SCREEN_COUNTDOWN:
            self.countdown_screen.update_preview(frame, blur=False)
    
    def _on_photo_button(self):
        """Handle photo button press."""
        print("[MainWindow] Photo button pressed")
        self.screen_stack.setCurrentIndex(self.SCREEN_COUNTDOWN)
        self.countdown_screen.start_countdown()
    
    def _on_settings_button(self):
        """Handle settings button press."""
        print("[MainWindow] Settings button pressed")
        self.screen_stack.setCurrentIndex(self.SCREEN_SETTINGS)
    
    def _on_countdown_finished(self):
        """Handle countdown completion - capture photo."""
        print("[MainWindow] Countdown finished, capturing photo...")
        
        if self.camera:
            result = self.camera.capture_photo()
            
            if result.success and result.image_data:
                self.last_photo_data = result.image_data
                
                # Save locally if enabled
                if self.settings.storage.save_locally:
                    self._save_photo_locally(result.image_data)
                
                # Show review screen
                self.review_screen.set_photo(result.image_data)
                self.screen_stack.setCurrentIndex(self.SCREEN_REVIEW)
                self.review_screen.start_review_timer()
                
                # Upload if enabled
                if self.settings.upload.upload_on_capture and self.uploader:
                    self._upload_photo(result.image_data)
            else:
                print(f"[MainWindow] Capture failed: {result.error_message}")
                # Return to idle on failure
                self.screen_stack.setCurrentIndex(self.SCREEN_IDLE)
    
    def _save_photo_locally(self, image_data: bytes):
        """Save photo to local storage."""
        try:
            photos_dir = ensure_photos_dir(self.settings)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.settings.storage.filename_pattern.replace(
                "{timestamp}", timestamp
            )
            filepath = photos_dir / filename
            
            with open(filepath, "wb") as f:
                f.write(image_data)
            
            print(f"[MainWindow] Photo saved: {filepath}")
            
        except Exception as e:
            print(f"[MainWindow] Failed to save photo: {e}")
    
    def _upload_photo(self, image_data: bytes):
        """Upload photo via REST API."""
        if self.uploader:
            # Generate filename for upload
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}.jpg"
            
            # Upload in background
            self.uploader.upload_async(image_data, filename)
    
    def _on_review_finished(self):
        """Handle review timer completion."""
        print("[MainWindow] Review finished, returning to idle")
        self.screen_stack.setCurrentIndex(self.SCREEN_IDLE)
    
    def _on_settings_closed(self):
        """Handle settings screen close."""
        print("[MainWindow] Settings closed")
        self.screen_stack.setCurrentIndex(self.SCREEN_IDLE)
    
    def _on_settings_saved(self, new_settings: Settings):
        """Handle settings save."""
        print("[MainWindow] Settings saved")
        self.settings = new_settings
        save_settings(self.settings)
        
        # Update all screens with new settings
        self.idle_screen.refresh_settings(self.settings)
        self.countdown_screen.refresh_settings(self.settings)
        self.review_screen.refresh_settings(self.settings)
        self.settings_screen.refresh_settings(self.settings)
        
        # Update camera preview FPS if changed
        if self.camera_thread:
            self.camera_thread.fps = self.settings.camera.preview_fps
        
        # Reload theme if changed
        from pibox5.app import load_theme, get_app
        app = get_app()
        if app:
            load_theme(app, self.settings.ui.theme)
        
        # Reconfigure uploader
        self._setup_uploader()
        
        print(f"[MainWindow] Settings applied: countdown={self.settings.timing.countdown_seconds}s, review={self.settings.timing.review_seconds}s")
        
        self.screen_stack.setCurrentIndex(self.SCREEN_IDLE)
    
    def closeEvent(self, event):
        """Handle window close."""
        print("[MainWindow] Closing...")
        
        # Stop camera thread
        if self.camera_thread:
            self.camera_thread.stop()
        
        # Disconnect camera
        if self.camera:
            self.camera.disconnect()
        
        event.accept()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        # ESC to exit fullscreen or quit
        if event.key() == Qt.Key.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.close()
        
        # F11 to toggle fullscreen
        elif event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        
        # Space to trigger photo (for testing)
        elif event.key() == Qt.Key.Key_Space:
            if self.screen_stack.currentIndex() == self.SCREEN_IDLE:
                self._on_photo_button()
        
        else:
            super().keyPressEvent(event)
