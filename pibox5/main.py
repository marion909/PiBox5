#!/usr/bin/env python3
"""
PiBox5 Photo Booth - Main Entry Point

Launch the photo booth application.
"""

import sys
import argparse
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PiBox5 Photo Booth Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--dummy-camera",
        action="store_true",
        help="Use dummy camera for testing (no real camera needed)",
    )
    
    parser.add_argument(
        "--windowed",
        action="store_true",
        help="Run in windowed mode instead of fullscreen",
    )
    
    parser.add_argument(
        "--settings",
        type=Path,
        help="Path to custom settings file",
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="PiBox5 1.0.0",
    )
    
    return parser.parse_args()


def main():
    """Main entry point for PiBox5."""
    args = parse_args()
    
    # Set up debug logging if requested
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        print("[PiBox5] Debug mode enabled")
    
    # Import Qt application
    from pibox5.app import create_app, run_app
    
    # Load settings
    from pibox5.config import load_settings
    settings = load_settings(args.settings)
    
    # Override settings from command line
    if args.dummy_camera:
        settings.camera.use_dummy = True
    if args.windowed:
        settings.ui.fullscreen = False
    
    # Create and run application
    app = create_app(settings)
    return run_app(app)


if __name__ == "__main__":
    sys.exit(main())
