"""
Dummy camera implementation for testing without real hardware.

Generates synthetic preview frames and simulated captures.
"""

import time
import random
from pathlib import Path
from typing import Optional, List
from datetime import datetime

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .base import CameraBase, CameraConfig, CaptureResult


class DummyCamera(CameraBase):
    """
    Dummy camera for testing and development.
    
    Generates colorful animated preview frames and
    simulated photo captures with timestamps.
    """
    
    def __init__(self, width: int = 800, height: int = 480):
        super().__init__()
        self.width = width
        self.height = height
        self._frame_count = 0
        self._start_time = time.time()
        
        # Simulated camera settings
        self._settings = {
            "iso": CameraConfig(
                name="iso",
                label="ISO",
                value="400",
                choices=["auto", "100", "200", "400", "800", "1600"],
            ),
            "aperture": CameraConfig(
                name="aperture",
                label="Blende",
                value="5.6",
                choices=["auto", "2.8", "4.0", "5.6", "8.0", "11", "16"],
            ),
            "shutterspeed": CameraConfig(
                name="shutterspeed",
                label="Verschlusszeit",
                value="1/125",
                choices=["auto", "1/30", "1/60", "1/125", "1/250", "1/500"],
            ),
            "imageformat": CameraConfig(
                name="imageformat",
                label="Bildqualität",
                value="Large Fine JPEG",
                choices=["Large Fine JPEG", "Large Normal JPEG", "RAW"],
            ),
        }
    
    def connect(self) -> bool:
        """Simulate camera connection."""
        print("[DummyCamera] Connecting to virtual camera...")
        time.sleep(0.5)  # Simulate connection delay
        self._connected = True
        self._start_time = time.time()
        print("[DummyCamera] Connected successfully!")
        return True
    
    def disconnect(self) -> None:
        """Simulate camera disconnection."""
        print("[DummyCamera] Disconnecting...")
        self._connected = False
        self._preview_active = False
    
    def get_preview_frame(self) -> Optional[np.ndarray]:
        """
        Generate an animated preview frame.
        
        Creates a colorful gradient with moving elements
        to simulate a live camera feed.
        """
        if not self._connected:
            return None
        
        self._frame_count += 1
        elapsed = time.time() - self._start_time
        
        # Create base gradient
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Animated gradient background
        for y in range(self.height):
            for x in range(self.width):
                # Create smooth color transitions
                r = int(128 + 127 * np.sin(elapsed * 0.5 + x * 0.01))
                g = int(128 + 127 * np.sin(elapsed * 0.7 + y * 0.01))
                b = int(128 + 127 * np.sin(elapsed * 0.3 + (x + y) * 0.005))
                frame[y, x] = [b, g, r]  # BGR format
        
        # Add some moving circles to simulate activity
        center_x = int(self.width / 2 + 200 * np.sin(elapsed * 1.5))
        center_y = int(self.height / 2 + 100 * np.cos(elapsed * 1.2))
        
        # Draw circle using numpy
        y_coords, x_coords = np.ogrid[:self.height, :self.width]
        mask = (x_coords - center_x) ** 2 + (y_coords - center_y) ** 2 <= 50 ** 2
        frame[mask] = [255, 255, 255]
        
        # Add frame counter text using PIL
        pil_image = Image.fromarray(frame[:, :, ::-1])  # BGR to RGB
        draw = ImageDraw.Draw(pil_image)
        
        # Try to use a nice font, fall back to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except OSError:
            font = ImageFont.load_default()
        
        # Draw info text
        text = f"DUMMY CAMERA - Frame {self._frame_count}"
        draw.text((20, 20), text, fill=(255, 255, 255), font=font)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        draw.text((20, 50), timestamp, fill=(255, 255, 0), font=font)
        
        # Convert back to BGR numpy array
        frame = np.array(pil_image)[:, :, ::-1]
        
        return frame
    
    def capture_photo(self) -> CaptureResult:
        """
        Simulate photo capture.
        
        Generates a high-resolution test image with timestamp.
        """
        if not self._connected:
            return CaptureResult(
                success=False,
                error_message="Camera not connected",
            )
        
        print("[DummyCamera] Capturing photo...")
        time.sleep(0.3)  # Simulate capture delay
        
        # Generate a test image
        img_width, img_height = 1920, 1280
        image = Image.new("RGB", (img_width, img_height), color=(50, 50, 80))
        draw = ImageDraw.Draw(image)
        
        # Try to use a nice font
        try:
            font_large = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72
            )
            font_medium = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36
            )
        except OSError:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Draw gradient background
        for y in range(img_height):
            r = int(50 + (y / img_height) * 100)
            g = int(50 + (y / img_height) * 80)
            b = int(80 + (y / img_height) * 120)
            draw.line([(0, y), (img_width, y)], fill=(r, g, b))
        
        # Draw decorative elements
        draw.ellipse(
            [img_width // 2 - 300, img_height // 2 - 200,
             img_width // 2 + 300, img_height // 2 + 200],
            outline=(255, 255, 255),
            width=5
        )
        
        # Add text
        title = "PiBox5 Photo Booth"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Center the text
        draw.text(
            (img_width // 2, img_height // 2 - 50),
            title,
            fill=(255, 255, 255),
            font=font_large,
            anchor="mm"
        )
        draw.text(
            (img_width // 2, img_height // 2 + 50),
            timestamp,
            fill=(200, 200, 200),
            font=font_medium,
            anchor="mm"
        )
        
        # Add camera settings info
        settings_text = f"ISO: {self._settings['iso'].value} | f/{self._settings['aperture'].value}"
        draw.text(
            (img_width // 2, img_height - 50),
            settings_text,
            fill=(150, 150, 150),
            font=font_medium,
            anchor="mm"
        )
        
        # Convert to bytes
        from io import BytesIO
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=95)
        image_data = buffer.getvalue()
        
        print(f"[DummyCamera] Photo captured! Size: {len(image_data)} bytes")
        
        return CaptureResult(
            success=True,
            image_data=image_data,
        )
    
    def get_config(self, name: str) -> Optional[CameraConfig]:
        """Get a camera configuration option."""
        return self._settings.get(name)
    
    def set_config(self, name: str, value: str) -> bool:
        """Set a camera configuration option."""
        if name in self._settings:
            config = self._settings[name]
            if value in config.choices:
                self._settings[name] = CameraConfig(
                    name=config.name,
                    label=config.label,
                    value=value,
                    choices=config.choices,
                    readonly=config.readonly,
                )
                print(f"[DummyCamera] Set {name} = {value}")
                return True
            print(f"[DummyCamera] Invalid value '{value}' for {name}")
            return False
        print(f"[DummyCamera] Unknown config: {name}")
        return False
    
    def list_configs(self) -> List[str]:
        """List all available configuration options."""
        return list(self._settings.keys())
    
    def get_camera_info(self) -> dict:
        """Get camera information."""
        info = super().get_camera_info()
        info.update({
            "model": "PiBox5 Dummy Camera",
            "serial": "DUMMY-001",
            "resolution": f"{self.width}x{self.height}",
            "frame_count": self._frame_count,
        })
        return info
