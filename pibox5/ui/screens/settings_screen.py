"""
Settings screen with touch-friendly configuration UI.

Provides access to all application settings via tabs.
"""

from typing import TYPE_CHECKING, Optional
from copy import deepcopy

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QScrollArea,
    QFormLayout,
    QSpinBox,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QSlider,
    QGroupBox,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal

from pibox5.config import Settings

if TYPE_CHECKING:
    from pibox5.ui.main_window import MainWindow


class SettingsScreen(QWidget):
    """
    Settings screen with tabbed configuration interface.
    
    Features:
    - Touch-friendly controls (large buttons, sliders)
    - Tabs for different setting categories
    - Apply/Cancel buttons
    """
    
    # Signals
    settings_closed = pyqtSignal()
    settings_saved = pyqtSignal(Settings)
    
    def __init__(self, settings: Settings, main_window: "MainWindow"):
        super().__init__()
        
        self.settings = settings
        self.main_window = main_window
        self._temp_settings: Optional[Settings] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the user interface."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a5e;
                background-color: #16213e;
                border-radius: 10px;
            }
            QTabBar::tab {
                background-color: #0f3460;
                color: white;
                padding: 15px 30px;
                margin-right: 5px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-size: 16px;
            }
            QTabBar::tab:selected {
                background-color: #e94560;
            }
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #3a3a5e;
                border-radius: 10px;
                margin-top: 20px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
            }
            QLabel {
                font-size: 16px;
            }
            QSpinBox, QComboBox, QLineEdit {
                background-color: #0f3460;
                border: 2px solid #3a3a5e;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 16px;
                min-height: 30px;
                min-width: 150px;
            }
            QSpinBox:focus, QComboBox:focus, QLineEdit:focus {
                border-color: #e94560;
            }
            QCheckBox {
                font-size: 16px;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 30px;
                height: 30px;
            }
            QSlider::groove:horizontal {
                height: 10px;
                background: #0f3460;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #e94560;
                width: 30px;
                height: 30px;
                margin: -10px 0;
                border-radius: 15px;
            }
            QPushButton {
                background-color: #0f3460;
                border: none;
                border-radius: 10px;
                padding: 15px 30px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a4a7a;
            }
            QPushButton#saveButton {
                background-color: #2ecc71;
            }
            QPushButton#saveButton:hover {
                background-color: #27ae60;
            }
            QPushButton#cancelButton {
                background-color: #e74c3c;
            }
            QPushButton#cancelButton:hover {
                background-color: #c0392b;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = QLabel("⚙️ Einstellungen")
        header.setStyleSheet("font-size: 32px; font-weight: bold;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self._create_general_tab()
        self._create_camera_tab()
        self._create_upload_tab()
        
        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        self.cancel_button = QPushButton("✕ Abbrechen")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        self.save_button = QPushButton("✓ Speichern")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
    
    def _create_general_tab(self):
        """Create the general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)
        
        # Timing group
        timing_group = QGroupBox("⏱️ Zeiteinstellungen")
        timing_layout = QFormLayout(timing_group)
        timing_layout.setSpacing(15)
        
        # Countdown seconds
        self.countdown_spin = QSpinBox()
        self.countdown_spin.setRange(1, 10)
        self.countdown_spin.setSuffix(" Sekunden")
        timing_layout.addRow("Countdown:", self.countdown_spin)
        
        # Review seconds
        self.review_spin = QSpinBox()
        self.review_spin.setRange(1, 30)
        self.review_spin.setSuffix(" Sekunden")
        timing_layout.addRow("Foto-Anzeige:", self.review_spin)
        
        content_layout.addWidget(timing_group)
        
        # UI group
        ui_group = QGroupBox("🎨 Oberfläche")
        ui_layout = QFormLayout(ui_group)
        ui_layout.setSpacing(15)
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["default", "dark"])
        ui_layout.addRow("Theme:", self.theme_combo)
        
        # Button size
        self.button_size_spin = QSpinBox()
        self.button_size_spin.setRange(100, 300)
        self.button_size_spin.setSuffix(" px")
        self.button_size_spin.setSingleStep(10)
        ui_layout.addRow("Button-Größe:", self.button_size_spin)
        
        # Blur radius
        self.blur_spin = QSpinBox()
        self.blur_spin.setRange(5, 50)
        self.blur_spin.setSuffix(" px")
        ui_layout.addRow("Blur-Stärke:", self.blur_spin)
        
        # Show settings button
        self.show_settings_check = QCheckBox("Einstellungs-Button anzeigen")
        ui_layout.addRow("", self.show_settings_check)
        
        content_layout.addWidget(ui_group)
        
        # Storage group
        storage_group = QGroupBox("💾 Speicherung")
        storage_layout = QFormLayout(storage_group)
        storage_layout.setSpacing(15)
        
        self.save_locally_check = QCheckBox("Lokal speichern")
        storage_layout.addRow("", self.save_locally_check)
        
        self.photos_dir_edit = QLineEdit()
        self.photos_dir_edit.setPlaceholderText("~/Pictures/PiBox5")
        storage_layout.addRow("Speicherort:", self.photos_dir_edit)
        
        content_layout.addWidget(storage_group)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tabs.addTab(tab, "🏠 Allgemein")
    
    def _create_camera_tab(self):
        """Create the camera settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)
        
        # Camera settings group
        camera_group = QGroupBox("📷 Kamera-Einstellungen")
        camera_layout = QFormLayout(camera_group)
        camera_layout.setSpacing(15)
        
        # ISO
        self.iso_combo = QComboBox()
        self.iso_combo.addItems(["auto", "100", "200", "400", "800", "1600"])
        camera_layout.addRow("ISO:", self.iso_combo)
        
        # Aperture
        self.aperture_combo = QComboBox()
        self.aperture_combo.addItems(["auto", "2.8", "4.0", "5.6", "8.0", "11", "16"])
        camera_layout.addRow("Blende:", self.aperture_combo)
        
        # Shutter speed
        self.shutter_combo = QComboBox()
        self.shutter_combo.addItems(["auto", "1/30", "1/60", "1/125", "1/250", "1/500"])
        camera_layout.addRow("Verschlusszeit:", self.shutter_combo)
        
        # Preview FPS
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(5, 30)
        self.fps_spin.setSuffix(" FPS")
        camera_layout.addRow("Vorschau-FPS:", self.fps_spin)
        
        content_layout.addWidget(camera_group)
        
        # Debug group
        debug_group = QGroupBox("🔧 Entwicklung")
        debug_layout = QFormLayout(debug_group)
        debug_layout.setSpacing(15)
        
        self.dummy_camera_check = QCheckBox("Dummy-Kamera verwenden (Test)")
        debug_layout.addRow("", self.dummy_camera_check)
        
        content_layout.addWidget(debug_group)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tabs.addTab(tab, "📷 Kamera")
    
    def _create_upload_tab(self):
        """Create the upload settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)
        
        # Upload settings group
        upload_group = QGroupBox("☁️ Upload-Einstellungen")
        upload_layout = QFormLayout(upload_group)
        upload_layout.setSpacing(15)
        
        # Enable upload
        self.upload_enabled_check = QCheckBox("Upload aktivieren")
        upload_layout.addRow("", self.upload_enabled_check)
        
        # URL
        self.upload_url_edit = QLineEdit()
        self.upload_url_edit.setPlaceholderText("https://api.example.com/upload")
        upload_layout.addRow("API-URL:", self.upload_url_edit)
        
        # API Key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Ihr API-Schlüssel")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        upload_layout.addRow("API-Key:", self.api_key_edit)
        
        # Auto upload
        self.auto_upload_check = QCheckBox("Automatisch nach Aufnahme hochladen")
        upload_layout.addRow("", self.auto_upload_check)
        
        # Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 120)
        self.timeout_spin.setSuffix(" Sekunden")
        upload_layout.addRow("Timeout:", self.timeout_spin)
        
        # Retry count
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(0, 10)
        self.retry_spin.setSuffix(" Versuche")
        upload_layout.addRow("Wiederholungen:", self.retry_spin)
        
        content_layout.addWidget(upload_group)
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tabs.addTab(tab, "☁️ Upload")
    
    def showEvent(self, event):
        """Load current settings when screen is shown."""
        super().showEvent(event)
        self._load_settings()
    
    def _load_settings(self):
        """Load current settings into UI controls."""
        s = self.settings
        
        # Timing
        self.countdown_spin.setValue(s.timing.countdown_seconds)
        self.review_spin.setValue(s.timing.review_seconds)
        
        # UI
        self.theme_combo.setCurrentText(s.ui.theme)
        self.button_size_spin.setValue(s.ui.button_size)
        self.blur_spin.setValue(s.ui.blur_radius)
        self.show_settings_check.setChecked(s.ui.show_settings_button)
        
        # Storage
        self.save_locally_check.setChecked(s.storage.save_locally)
        self.photos_dir_edit.setText(s.storage.photos_dir)
        
        # Camera
        self.iso_combo.setCurrentText(s.camera.iso)
        self.aperture_combo.setCurrentText(s.camera.aperture)
        self.shutter_combo.setCurrentText(s.camera.shutter_speed)
        self.fps_spin.setValue(s.camera.preview_fps)
        self.dummy_camera_check.setChecked(s.camera.use_dummy)
        
        # Upload
        self.upload_enabled_check.setChecked(s.upload.enabled)
        self.upload_url_edit.setText(s.upload.url)
        self.api_key_edit.setText(s.upload.api_key)
        self.auto_upload_check.setChecked(s.upload.upload_on_capture)
        self.timeout_spin.setValue(s.upload.timeout_seconds)
        self.retry_spin.setValue(s.upload.retry_count)
    
    def _save_settings(self) -> Settings:
        """Save UI values to settings object."""
        s = deepcopy(self.settings)
        
        # Timing
        s.timing.countdown_seconds = self.countdown_spin.value()
        s.timing.review_seconds = self.review_spin.value()
        
        # UI
        s.ui.theme = self.theme_combo.currentText()
        s.ui.button_size = self.button_size_spin.value()
        s.ui.blur_radius = self.blur_spin.value()
        s.ui.show_settings_button = self.show_settings_check.isChecked()
        
        # Storage
        s.storage.save_locally = self.save_locally_check.isChecked()
        s.storage.photos_dir = self.photos_dir_edit.text()
        
        # Camera
        s.camera.iso = self.iso_combo.currentText()
        s.camera.aperture = self.aperture_combo.currentText()
        s.camera.shutter_speed = self.shutter_combo.currentText()
        s.camera.preview_fps = self.fps_spin.value()
        s.camera.use_dummy = self.dummy_camera_check.isChecked()
        
        # Upload
        s.upload.enabled = self.upload_enabled_check.isChecked()
        s.upload.url = self.upload_url_edit.text()
        s.upload.api_key = self.api_key_edit.text()
        s.upload.upload_on_capture = self.auto_upload_check.isChecked()
        s.upload.timeout_seconds = self.timeout_spin.value()
        s.upload.retry_count = self.retry_spin.value()
        
        return s
    
    def _on_save(self):
        """Handle save button click."""
        new_settings = self._save_settings()
        self.settings_saved.emit(new_settings)
    
    def _on_cancel(self):
        """Handle cancel button click."""
        self.settings_closed.emit()
