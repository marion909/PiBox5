"""
PiBox5 Application setup and initialization.

Creates the Qt application and main window.
"""

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from pibox5.config import Settings
from pibox5.ui import MainWindow


# Global application instance
_app: Optional[QApplication] = None
_main_window: Optional[MainWindow] = None


def create_app(settings: Settings) -> QApplication:
    """
    Create the Qt application.
    
    Args:
        settings: Application settings.
        
    Returns:
        QApplication instance.
    """
    global _app, _main_window
    
    # Set high DPI scaling attributes before creating app
    # These are needed for proper touch screen support
    
    # Create application
    _app = QApplication(sys.argv)
    _app.setApplicationName("PiBox5")
    _app.setApplicationVersion("1.0.0")
    _app.setOrganizationName("PiBox5")
    
    # Set default font
    font = QFont("Segoe UI", 12)
    if not font.exactMatch():
        font = QFont("DejaVu Sans", 12)
    _app.setFont(font)
    
    # Load theme
    load_theme(_app, settings.ui.theme)
    
    # Create main window
    _main_window = MainWindow(settings)
    
    # Set fullscreen or windowed mode
    if settings.ui.fullscreen:
        _main_window.showFullScreen()
    else:
        _main_window.resize(800, 480)  # 7" display resolution
        _main_window.show()
    
    return _app


def load_theme(app: QApplication, theme_name: str) -> bool:
    """
    Load a QSS theme.
    
    Args:
        app: QApplication instance.
        theme_name: Name of the theme ("default" or "dark").
        
    Returns:
        True if theme loaded successfully.
    """
    # Get theme file path
    theme_dir = Path(__file__).parent / "ui" / "themes"
    theme_file = theme_dir / f"{theme_name}.qss"
    
    if not theme_file.exists():
        print(f"[App] Theme file not found: {theme_file}")
        return False
    
    try:
        with open(theme_file, "r", encoding="utf-8") as f:
            stylesheet = f.read()
        app.setStyleSheet(stylesheet)
        print(f"[App] Loaded theme: {theme_name}")
        return True
    except Exception as e:
        print(f"[App] Failed to load theme: {e}")
        return False


def run_app(app: QApplication) -> int:
    """
    Run the Qt application event loop.
    
    Args:
        app: QApplication instance.
        
    Returns:
        Exit code.
    """
    return app.exec()


def get_app() -> Optional[QApplication]:
    """Get the current QApplication instance."""
    return _app


def get_main_window() -> Optional[MainWindow]:
    """Get the main window instance."""
    return _main_window
