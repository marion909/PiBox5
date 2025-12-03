"""Camera module for PiBox5."""

from .base import CameraBase
from .dummy_camera import DummyCamera

__all__ = ["CameraBase", "DummyCamera"]

# gphoto2_camera is imported conditionally to handle missing gphoto2 library
try:
    from .gphoto2_camera import GPhoto2Camera
    __all__.append("GPhoto2Camera")
except ImportError:
    GPhoto2Camera = None
