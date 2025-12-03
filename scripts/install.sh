#!/bin/bash
#
# PiBox5 Photo Booth - One-Click Installer
# For Raspberry Pi 5 with Raspberry Pi OS (Bookworm)
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/marion909/PiBox5/main/scripts/install.sh | bash
#   or
#   ./scripts/install.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PIBOX_DIR="${HOME}/pibox5"
VENV_DIR="${HOME}/.pibox5-venv"
CONFIG_DIR="${HOME}/.config/pibox5"
AUTOSTART_DIR="${HOME}/.config/autostart"

# Print colored message
print_msg() {
    echo -e "${2}${1}${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Check if running on Raspberry Pi
check_raspberry_pi() {
    if [ ! -f /proc/device-tree/model ]; then
        print_msg "⚠️  Warning: Could not detect Raspberry Pi. Continuing anyway..." "${YELLOW}"
        return
    fi
    
    # Remove null bytes from model string
    MODEL=$(tr -d '\0' < /proc/device-tree/model)
    print_msg "📍 Detected: ${MODEL}" "${GREEN}"
}

# Check for root
check_not_root() {
    if [ "$EUID" -eq 0 ]; then
        print_msg "❌ Please do not run this script as root!" "${RED}"
        print_msg "   Run as normal user: ./install.sh" "${RED}"
        exit 1
    fi
}

# Welcome message
show_welcome() {
    clear
    echo ""
    echo -e "${GREEN}"
    echo "  ██████╗ ██╗██████╗  ██████╗ ██╗  ██╗███████╗"
    echo "  ██╔══██╗██║██╔══██╗██╔═══██╗╚██╗██╔╝██╔════╝"
    echo "  ██████╔╝██║██████╔╝██║   ██║ ╚███╔╝ ███████╗"
    echo "  ██╔═══╝ ██║██╔══██╗██║   ██║ ██╔██╗ ╚════██║"
    echo "  ██║     ██║██████╔╝╚██████╔╝██╔╝ ██╗███████║"
    echo "  ╚═╝     ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${BLUE}  Modern Photo Booth for Raspberry Pi 5${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Update system
update_system() {
    print_header "📦 Updating System Packages"
    
    print_msg "Running apt update..." "${YELLOW}"
    sudo apt update
    
    print_msg "Upgrading packages..." "${YELLOW}"
    sudo apt upgrade -y
    
    print_msg "✓ System updated" "${GREEN}"
}

# Install system dependencies
install_dependencies() {
    print_header "🔧 Installing System Dependencies"
    
    PACKAGES=(
        # Python
        python3-pip
        python3-venv
        python3-dev
        
        # gPhoto2 for camera control
        gphoto2
        libgphoto2-dev
        
        # Qt6/OpenGL dependencies (Bookworm compatible)
        libgl1
        libglx-mesa0
        libegl1
        libgles2
        libxcb-xinerama0
        libxcb-cursor0
        libxkbcommon-x11-0
        
        # Image processing
        libjpeg-dev
        libpng-dev
        libtiff-dev
        
        # Touch screen support
        libts-bin
        
        # Fonts
        fonts-dejavu-core
        
        # Additional Qt dependencies
        libxcb-icccm4
        libxcb-image0
        libxcb-keysyms1
        libxcb-randr0
        libxcb-render-util0
        libxcb-shape0
    )
    
    print_msg "Installing: ${PACKAGES[*]}" "${YELLOW}"
    sudo apt install -y "${PACKAGES[@]}"
    
    print_msg "✓ Dependencies installed" "${GREEN}"
}

# Create Python virtual environment
setup_python_env() {
    print_header "🐍 Setting Up Python Environment"
    
    # Remove existing venv if exists
    if [ -d "${VENV_DIR}" ]; then
        print_msg "Removing existing virtual environment..." "${YELLOW}"
        rm -rf "${VENV_DIR}"
    fi
    
    # Create new venv
    print_msg "Creating virtual environment at ${VENV_DIR}..." "${YELLOW}"
    python3 -m venv "${VENV_DIR}"
    
    # Activate and upgrade pip
    source "${VENV_DIR}/bin/activate"
    pip install --upgrade pip wheel setuptools
    
    print_msg "✓ Python environment ready" "${GREEN}"
}

# Install PiBox5
install_pibox5() {
    print_header "📸 Installing PiBox5"
    
    # Activate venv
    source "${VENV_DIR}/bin/activate"
    
    # Check if we're in the pibox5 directory
    if [ -f "pyproject.toml" ]; then
        print_msg "Installing from local directory..." "${YELLOW}"
        pip install -e .
    else
        # Clone from GitHub (placeholder URL)
        print_msg "Cloning from repository..." "${YELLOW}"
        if [ -d "${PIBOX_DIR}" ]; then
            rm -rf "${PIBOX_DIR}"
        fi
        git clone https://github.com/marion909/PiBox5.git "${PIBOX_DIR}"
        cd "${PIBOX_DIR}"
        pip install -e .
    fi
    
    print_msg "✓ PiBox5 installed" "${GREEN}"
}

# Install Python packages
install_python_packages() {
    print_header "📚 Installing Python Packages"
    
    source "${VENV_DIR}/bin/activate"
    
    # Install from requirements if available
    if [ -f "requirements.txt" ]; then
        print_msg "Installing from requirements.txt..." "${YELLOW}"
        pip install -r requirements.txt
    else
        # Manual installation
        PACKAGES=(
            PyQt6
            gphoto2
            Pillow
            opencv-python-headless
            numpy
            requests
            PyYAML
        )
        
        print_msg "Installing: ${PACKAGES[*]}" "${YELLOW}"
        pip install "${PACKAGES[@]}"
    fi
    
    print_msg "✓ Python packages installed" "${GREEN}"
}

# Create configuration
setup_config() {
    print_header "⚙️ Setting Up Configuration"
    
    # Create config directory
    mkdir -p "${CONFIG_DIR}"
    
    # Create default photos directory
    PHOTOS_DIR="${HOME}/Pictures/PiBox5"
    mkdir -p "${PHOTOS_DIR}"
    
    # Create default settings file if it doesn't exist
    SETTINGS_FILE="${CONFIG_DIR}/settings.yaml"
    if [ ! -f "${SETTINGS_FILE}" ]; then
        print_msg "Creating default settings..." "${YELLOW}"
        cat > "${SETTINGS_FILE}" << EOF
# PiBox5 Settings
ui:
  theme: "default"
  fullscreen: true
  show_settings_button: true
  button_size: 150
  blur_radius: 20

timing:
  countdown_seconds: 3
  review_seconds: 5

camera:
  use_dummy: false
  iso: "auto"
  preview_fps: 10

upload:
  enabled: false
  url: ""
  api_key: ""

storage:
  save_locally: true
  photos_dir: "${PHOTOS_DIR}"
EOF
    fi
    
    print_msg "✓ Configuration ready" "${GREEN}"
}

# Setup autostart
setup_autostart() {
    print_header "🚀 Configuring Autostart"
    
    read -p "Enable autostart on boot? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p "${AUTOSTART_DIR}"
        
        cat > "${AUTOSTART_DIR}/pibox5.desktop" << EOF
[Desktop Entry]
Type=Application
Name=PiBox5 Photo Booth
Comment=Modern Photo Booth Application
Exec=${VENV_DIR}/bin/python -m pibox5.main
Icon=camera-photo
Terminal=false
Categories=Graphics;Photography;
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF
        
        print_msg "✓ Autostart enabled" "${GREEN}"
        print_msg "  PiBox5 will start automatically on next boot" "${BLUE}"
    else
        print_msg "⏩ Autostart skipped" "${YELLOW}"
    fi
}

# Create desktop shortcut
create_shortcut() {
    print_header "🖥️ Creating Desktop Shortcut"
    
    DESKTOP_DIR="${HOME}/Desktop"
    mkdir -p "${DESKTOP_DIR}"
    
    cat > "${DESKTOP_DIR}/PiBox5.desktop" << EOF
[Desktop Entry]
Type=Application
Name=PiBox5 Photo Booth
Comment=Start the Photo Booth
Exec=${VENV_DIR}/bin/python -m pibox5.main
Icon=camera-photo
Terminal=false
Categories=Graphics;Photography;
EOF
    
    chmod +x "${DESKTOP_DIR}/PiBox5.desktop"
    
    print_msg "✓ Desktop shortcut created" "${GREEN}"
}

# Create launcher script
create_launcher() {
    print_header "📝 Creating Launcher Script"
    
    LAUNCHER="/usr/local/bin/pibox5"
    
    sudo tee "${LAUNCHER}" > /dev/null << EOF
#!/bin/bash
# PiBox5 Launcher
source ${VENV_DIR}/bin/activate
python -m pibox5.main "\$@"
EOF
    
    sudo chmod +x "${LAUNCHER}"
    
    print_msg "✓ Launcher created: pibox5" "${GREEN}"
    print_msg "  Run 'pibox5' from anywhere to start" "${BLUE}"
}

# Test camera connection
test_camera() {
    print_header "📷 Testing Camera Connection"
    
    print_msg "Detecting cameras..." "${YELLOW}"
    
    if gphoto2 --auto-detect 2>/dev/null | grep -q "usb"; then
        print_msg "✓ Camera detected!" "${GREEN}"
        gphoto2 --auto-detect
    else
        print_msg "⚠️  No camera detected" "${YELLOW}"
        print_msg "   Connect your camera and run: gphoto2 --auto-detect" "${BLUE}"
        print_msg "   You can still test with: pibox5 --dummy-camera" "${BLUE}"
    fi
}

# Show completion message
show_complete() {
    print_header "🎉 Installation Complete!"
    
    echo ""
    echo -e "${GREEN}PiBox5 has been successfully installed!${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${BLUE}Quick Start:${NC}"
    echo ""
    echo "  Start PiBox5:"
    echo "    pibox5"
    echo ""
    echo "  Start without camera (demo mode):"
    echo "    pibox5 --dummy-camera"
    echo ""
    echo "  Start in windowed mode:"
    echo "    pibox5 --windowed"
    echo ""
    echo -e "${BLUE}Useful Locations:${NC}"
    echo ""
    echo "  Settings:  ${CONFIG_DIR}/settings.yaml"
    echo "  Photos:    ${HOME}/Pictures/PiBox5/"
    echo "  Logs:      ${CONFIG_DIR}/pibox5.log"
    echo ""
    echo -e "${BLUE}Camera Tips:${NC}"
    echo ""
    echo "  - Set camera to Manual or Av/Tv mode"
    echo "  - Use USB 3.0 port for best performance"
    echo "  - Disable camera auto-power-off"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    read -p "Start PiBox5 now? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_msg "Starting PiBox5..." "${GREEN}"
        pibox5 --dummy-camera --windowed
    fi
}

# Main installation flow
main() {
    show_welcome
    
    check_not_root
    check_raspberry_pi
    
    echo ""
    read -p "Start installation? (y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_msg "Installation cancelled." "${YELLOW}"
        exit 0
    fi
    
    update_system
    install_dependencies
    setup_python_env
    install_python_packages
    install_pibox5
    setup_config
    setup_autostart
    create_shortcut
    create_launcher
    test_camera
    
    show_complete
}

# Run main
main "$@"
