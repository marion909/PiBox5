"""
Abstract base class for camera implementations.

Defines the interface that all camera backends must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path
import numpy as np


@dataclass
class CameraConfig:
    """Camera configuration option."""
    
    name: str
    label: str
    value: str
    choices: List[str]
    readonly: bool = False


@dataclass
class CaptureResult:
    """Result of a photo capture operation."""
    
    success: bool
    image_data: Optional[bytes] = None
    file_path: Optional[Path] = None
    error_message: Optional[str] = None


class CameraBase(ABC):
    """
    Abstract base class for camera implementations.
    
    Provides a common interface for different camera backends
    (gPhoto2, dummy camera for testing, etc.).
    """
    
    def __init__(self):
        self._connected = False
        self._preview_active = False
    
    @property
    def is_connected(self) -> bool:
        """Check if camera is connected."""
        return self._connected
    
    @property
    def is_preview_active(self) -> bool:
        """Check if live preview is active."""
        return self._preview_active
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the camera.
        
        Returns:
            True if connection successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the camera."""
        pass
    
    @abstractmethod
    def get_preview_frame(self) -> Optional[np.ndarray]:
        """
        Get a single preview frame from the camera.
        
        Returns:
            Preview frame as numpy array (BGR format) or None if unavailable.
        """
        pass
    
    @abstractmethod
    def capture_photo(self) -> CaptureResult:
        """
        Capture a full-resolution photo.
        
        Returns:
            CaptureResult with image data or error information.
        """
        pass
    
    @abstractmethod
    def get_config(self, name: str) -> Optional[CameraConfig]:
        """
        Get a camera configuration option.
        
        Args:
            name: Configuration option name (e.g., "iso", "aperture").
            
        Returns:
            CameraConfig object or None if not available.
        """
        pass
    
    @abstractmethod
    def set_config(self, name: str, value: str) -> bool:
        """
        Set a camera configuration option.
        
        Args:
            name: Configuration option name.
            value: New value to set.
            
        Returns:
            True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def list_configs(self) -> List[str]:
        """
        List all available configuration options.
        
        Returns:
            List of configuration option names.
        """
        pass
    
    def start_preview(self) -> bool:
        """
        Start live preview mode.
        
        Returns:
            True if preview started successfully.
        """
        self._preview_active = True
        return True
    
    def stop_preview(self) -> None:
        """Stop live preview mode."""
        self._preview_active = False
    
    def get_camera_info(self) -> Dict[str, Any]:
        """
        Get camera information.
        
        Returns:
            Dictionary with camera model, serial, etc.
        """
        return {
            "connected": self._connected,
            "preview_active": self._preview_active,
        }
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False
