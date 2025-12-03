"""
Settings management for PiBox5.

Provides dataclass-based settings with YAML persistence.
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
import yaml


# Default config directory
CONFIG_DIR = Path.home() / ".config" / "pibox5"
SETTINGS_FILE = CONFIG_DIR / "settings.yaml"


@dataclass
class UISettings:
    """User interface settings."""
    
    theme: str = "default"  # "default" or "dark"
    fullscreen: bool = True
    show_settings_button: bool = True
    button_size: int = 120  # Photo button diameter in pixels (optimized for 800x480)
    countdown_font_size: int = 140  # Countdown number font size (optimized for 800x480)
    blur_radius: int = 15  # Blur radius for idle preview


@dataclass
class TimingSettings:
    """Timing-related settings."""
    
    countdown_seconds: int = 3  # 1-10 seconds
    review_seconds: int = 5  # 1-30 seconds
    idle_timeout_minutes: int = 0  # 0 = disabled


@dataclass
class CameraSettings:
    """Camera configuration settings."""
    
    use_dummy: bool = False  # Use dummy camera for testing
    iso: str = "auto"  # "auto", "100", "200", "400", "800", "1600"
    aperture: str = "auto"  # f-stop value or "auto"
    shutter_speed: str = "auto"  # Shutter speed or "auto"
    image_quality: str = "large_fine"  # JPEG quality setting
    capture_target: str = "memory"  # "memory" or "card"
    preview_fps: int = 10  # Live preview target FPS


@dataclass
class UploadSettings:
    """REST API upload settings."""
    
    enabled: bool = False
    url: str = ""  # REST API endpoint URL
    api_key: str = ""  # API key or token
    upload_on_capture: bool = True  # Auto-upload after capture
    retry_count: int = 3  # Number of retry attempts
    timeout_seconds: int = 30  # Upload timeout


@dataclass
class StorageSettings:
    """Local storage settings."""
    
    save_locally: bool = True
    photos_dir: str = str(Path.home() / "Pictures" / "PiBox5")
    filename_pattern: str = "photo_{timestamp}.jpg"  # {timestamp}, {counter}


@dataclass
class Settings:
    """Main settings container with all configuration options."""
    
    ui: UISettings = field(default_factory=UISettings)
    timing: TimingSettings = field(default_factory=TimingSettings)
    camera: CameraSettings = field(default_factory=CameraSettings)
    upload: UploadSettings = field(default_factory=UploadSettings)
    storage: StorageSettings = field(default_factory=StorageSettings)
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        """Create settings from dictionary."""
        return cls(
            ui=UISettings(**data.get("ui", {})),
            timing=TimingSettings(**data.get("timing", {})),
            camera=CameraSettings(**data.get("camera", {})),
            upload=UploadSettings(**data.get("upload", {})),
            storage=StorageSettings(**data.get("storage", {})),
        )


def load_settings(path: Optional[Path] = None) -> Settings:
    """
    Load settings from YAML file.
    
    Args:
        path: Optional custom path to settings file.
        
    Returns:
        Settings object with loaded or default values.
    """
    settings_path = path or SETTINGS_FILE
    
    if settings_path.exists():
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return Settings.from_dict(data)
        except Exception as e:
            print(f"Warning: Could not load settings from {settings_path}: {e}")
            print("Using default settings.")
    
    return Settings()


def save_settings(settings: Settings, path: Optional[Path] = None) -> bool:
    """
    Save settings to YAML file.
    
    Args:
        settings: Settings object to save.
        path: Optional custom path to settings file.
        
    Returns:
        True if save was successful, False otherwise.
    """
    settings_path = path or SETTINGS_FILE
    
    try:
        # Ensure config directory exists
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(settings_path, "w", encoding="utf-8") as f:
            yaml.dump(
                settings.to_dict(),
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
        return True
    except Exception as e:
        print(f"Error saving settings to {settings_path}: {e}")
        return False


def ensure_photos_dir(settings: Settings) -> Path:
    """
    Ensure the photos directory exists.
    
    Args:
        settings: Settings object with storage configuration.
        
    Returns:
        Path to photos directory.
    """
    photos_path = Path(settings.storage.photos_dir)
    photos_path.mkdir(parents=True, exist_ok=True)
    return photos_path
