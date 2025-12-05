"""
gPhoto2 camera implementation for Canon EOS and other DSLR cameras.

Uses python-gphoto2 bindings to control the camera.
"""

import io
from pathlib import Path
from typing import Optional, List

import numpy as np
from PIL import Image

from .base import CameraBase, CameraConfig, CaptureResult

# Import gphoto2 with error handling
try:
    import gphoto2 as gp
    GPHOTO2_AVAILABLE = True
except ImportError:
    GPHOTO2_AVAILABLE = False
    gp = None


class GPhoto2Camera(CameraBase):
    """
    gPhoto2 camera implementation.
    
    Supports Canon EOS, Nikon, Sony, and other gPhoto2-compatible cameras.
    Provides live preview, photo capture, and camera settings control.
    """
    
    # Mapping of common config names to gPhoto2 paths
    CONFIG_MAPPING = {
        "iso": "/main/imgsettings/iso",
        "aperture": "/main/capturesettings/aperture",
        "shutterspeed": "/main/capturesettings/shutterspeed",
        "imageformat": "/main/imgsettings/imageformat",
        "imageformatsd": "/main/imgsettings/imageformatsd",
        "whitebalance": "/main/imgsettings/whitebalance",
        "focusmode": "/main/capturesettings/focusmode",
    }
    
    def __init__(self):
        super().__init__()
        
        if not GPHOTO2_AVAILABLE:
            raise ImportError(
                "gphoto2 library not available. "
                "Install with: pip install gphoto2"
            )
        
        self._camera: Optional[gp.Camera] = None
        self._context: Optional[gp.Context] = None
        self._model = "Unknown"
        self._serial = "Unknown"
    
    def connect(self) -> bool:
        """
        Connect to the camera via USB.
        
        Returns:
            True if connection successful.
        """
        try:
            # Initialize gPhoto2 context
            self._context = gp.Context()
            
            # Detect and initialize camera
            self._camera = gp.Camera()
            self._camera.init()
            
            # Get camera info
            abilities = self._camera.get_abilities()
            self._model = abilities.model
            
            # Try to get serial number
            try:
                config = self._camera.get_config()
                serial_widget = config.get_child_by_name("serialnumber")
                self._serial = serial_widget.get_value()
            except gp.GPhoto2Error:
                self._serial = "N/A"
            
            self._connected = True
            print(f"[GPhoto2] Connected to {self._model}")
            return True
            
        except gp.GPhoto2Error as e:
            print(f"[GPhoto2] Connection failed: {e}")
            self._connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the camera."""
        if self._camera is not None:
            try:
                self._camera.exit()
            except gp.GPhoto2Error:
                pass
            self._camera = None
        
        self._context = None
        self._connected = False
        self._preview_active = False
        print("[GPhoto2] Disconnected")
    
    def get_preview_frame(self) -> Optional[np.ndarray]:
        """
        Capture a preview frame from the camera's live view.
        
        Returns:
            Preview frame as BGR numpy array.
        """
        if not self._connected or self._camera is None:
            return None
        
        try:
            # Capture preview image - create CameraFile first
            camera_file = gp.CameraFile()
            self._camera.capture_preview(camera_file)
            
            # Get file data
            file_data = camera_file.get_data_and_size()
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(file_data))
            
            # Convert to BGR numpy array for OpenCV compatibility
            frame = np.array(image)
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # RGB to BGR
                frame = frame[:, :, ::-1]
            
            return frame
            
        except gp.GPhoto2Error as e:
            print(f"[GPhoto2] Preview capture failed: {e}")
            return None
    
    def _trigger_autofocus(self) -> bool:
        """
        Trigger autofocus on the camera.
        
        Returns:
            True if autofocus was triggered successfully.
        """
        if not self._connected or self._camera is None:
            return False
        
        try:
            # Get camera config
            config = self._camera.get_config()
            
            # Try different autofocus trigger methods
            # Method 1: Use autofocusdrive (Canon)
            try:
                af_widget = config.get_child_by_name("autofocusdrive")
                af_widget.set_value(1)
                self._camera.set_config(config)
                print("[GPhoto2] Autofocus triggered (autofocusdrive)")
                
                # Wait for focus to complete
                import time
                time.sleep(0.5)
                return True
            except gp.GPhoto2Error:
                pass
            
            # Method 2: Use eosremoterelease (Canon EOS)
            try:
                config = self._camera.get_config()  # Refresh config
                release_widget = config.get_child_by_name("eosremoterelease")
                # Press halfway to trigger AF
                release_widget.set_value("Press Half")
                self._camera.set_config(config)
                
                import time
                time.sleep(0.8)  # Wait for AF
                
                # Release
                config = self._camera.get_config()
                release_widget = config.get_child_by_name("eosremoterelease")
                release_widget.set_value("Release Full")
                self._camera.set_config(config)
                
                print("[GPhoto2] Autofocus triggered (eosremoterelease)")
                return True
            except gp.GPhoto2Error:
                pass
            
            # Method 3: Use capture target with AF
            print("[GPhoto2] No direct AF control, relying on camera AF mode")
            return False
            
        except gp.GPhoto2Error as e:
            print(f"[GPhoto2] Autofocus failed: {e}")
            return False
    
    def capture_photo(self) -> CaptureResult:
        """
        Capture a full-resolution photo.
        
        Returns:
            CaptureResult with image data.
        """
        if not self._connected or self._camera is None:
            return CaptureResult(
                success=False,
                error_message="Camera not connected",
            )
        
        try:
            print("[GPhoto2] Capturing photo...")
            
            # Trigger autofocus before capture
            self._trigger_autofocus()
            
            # Capture image
            file_path = self._camera.capture(gp.GP_CAPTURE_IMAGE)
            print(f"[GPhoto2] Captured: {file_path.folder}/{file_path.name}")
            
            # Download file from camera
            camera_file = gp.CameraFile()
            self._camera.file_get(
                file_path.folder,
                file_path.name,
                gp.GP_FILE_TYPE_NORMAL,
                camera_file,
            )
            
            # Get image data
            image_data = camera_file.get_data_and_size()
            
            # Optionally delete from camera
            try:
                self._camera.file_delete(
                    file_path.folder,
                    file_path.name,
                )
            except gp.GPhoto2Error:
                pass  # Some cameras don't support deletion
            
            print(f"[GPhoto2] Photo captured! Size: {len(image_data)} bytes")
            
            return CaptureResult(
                success=True,
                image_data=bytes(image_data),
            )
            
        except gp.GPhoto2Error as e:
            error_msg = f"Capture failed: {e}"
            print(f"[GPhoto2] {error_msg}")
            return CaptureResult(
                success=False,
                error_message=error_msg,
            )
    
    def get_config(self, name: str) -> Optional[CameraConfig]:
        """
        Get a camera configuration option.
        
        Args:
            name: Config name (e.g., "iso", "aperture").
        """
        if not self._connected or self._camera is None:
            return None
        
        # Get gPhoto2 config path
        config_path = self.CONFIG_MAPPING.get(name)
        if not config_path:
            config_path = name  # Use name directly if not in mapping
        
        try:
            config = self._camera.get_config()
            widget = config.get_child_by_name(config_path.split("/")[-1])
            
            # Get current value
            value = widget.get_value()
            
            # Get choices if available
            choices = []
            widget_type = widget.get_type()
            if widget_type in (gp.GP_WIDGET_RADIO, gp.GP_WIDGET_MENU):
                for i in range(widget.count_choices()):
                    choices.append(widget.get_choice(i))
            
            return CameraConfig(
                name=name,
                label=widget.get_label(),
                value=str(value),
                choices=choices,
                readonly=widget.get_readonly(),
            )
            
        except gp.GPhoto2Error as e:
            print(f"[GPhoto2] Failed to get config '{name}': {e}")
            return None
    
    def set_config(self, name: str, value: str) -> bool:
        """
        Set a camera configuration option.
        
        Args:
            name: Config name.
            value: New value.
        """
        if not self._connected or self._camera is None:
            return False
        
        config_path = self.CONFIG_MAPPING.get(name)
        if not config_path:
            config_path = name
        
        try:
            config = self._camera.get_config()
            widget = config.get_child_by_name(config_path.split("/")[-1])
            
            # Check if readonly
            if widget.get_readonly():
                print(f"[GPhoto2] Config '{name}' is read-only")
                return False
            
            # Set value
            widget.set_value(value)
            self._camera.set_config(config)
            
            print(f"[GPhoto2] Set {name} = {value}")
            return True
            
        except gp.GPhoto2Error as e:
            print(f"[GPhoto2] Failed to set config '{name}': {e}")
            return False
    
    def list_configs(self) -> List[str]:
        """List all available configuration options."""
        if not self._connected or self._camera is None:
            return []
        
        try:
            config = self._camera.get_config()
            configs = []
            self._list_config_recursive(config, configs)
            return configs
        except gp.GPhoto2Error:
            return []
    
    def _list_config_recursive(
        self, widget, configs: List[str], path: str = ""
    ) -> None:
        """Recursively list configuration widgets."""
        name = widget.get_name()
        current_path = f"{path}/{name}" if path else name
        
        widget_type = widget.get_type()
        
        # Only add configurable widgets
        if widget_type in (
            gp.GP_WIDGET_TEXT,
            gp.GP_WIDGET_RADIO,
            gp.GP_WIDGET_MENU,
            gp.GP_WIDGET_TOGGLE,
            gp.GP_WIDGET_RANGE,
        ):
            configs.append(current_path)
        
        # Recurse into sections
        if widget_type in (gp.GP_WIDGET_SECTION, gp.GP_WIDGET_WINDOW):
            for i in range(widget.count_children()):
                child = widget.get_child(i)
                self._list_config_recursive(child, configs, current_path)
    
    def get_camera_info(self) -> dict:
        """Get camera information."""
        info = super().get_camera_info()
        info.update({
            "model": self._model,
            "serial": self._serial,
            "backend": "gPhoto2",
            "gphoto2_available": GPHOTO2_AVAILABLE,
        })
        return info
