# PiBox5 - Modern Photo Booth for Raspberry Pi 5

Eine elegante Fotobox-Anwendung für Raspberry Pi 5 mit Canon DSLR-Unterstützung.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- 🎥 **Live-Vorschau** mit Blur-Effekt im Idle-Modus
- 📸 **Countdown-Timer** (konfigurierbar 1-10 Sekunden)
- 🖼️ **Review-Screen** mit automatischem Timeout
- ⚙️ **Touch-freundliches Settings-Menü**
- 📤 **REST-API Upload** für automatischen Foto-Upload
- 🎨 **Theme-System** mit hellen und dunklen Themes
- 📷 **Canon EOS Unterstützung** via gPhoto2

## Hardware-Anforderungen

- Raspberry Pi 5 (4GB+ RAM empfohlen)
- 7" OSOYOO DSI Touch Display (800x480)
- Canon EOS 1000D (oder andere gPhoto2-kompatible Kamera)
- USB-Kabel für Kamera

## Quick Install

```bash
# One-Click Installation
curl -sSL https://raw.githubusercontent.com/pibox5/pibox5/main/scripts/install.sh | bash

# Oder manuell:
git clone https://github.com/pibox5/pibox5.git
cd pibox5
./scripts/install.sh
```

## Manuelle Installation

### 1. System-Dependencies

```bash
sudo apt update
sudo apt install -y \
    python3-pip python3-venv \
    gphoto2 libgphoto2-dev \
    libgl1-mesa-glx libgles2-mesa \
    libxcb-xinerama0 libxcb-cursor0
```

### 2. Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Starten

```bash
# Mit echter Kamera
pibox5

# Ohne Kamera (Demo-Modus)
pibox5 --dummy-camera
```

## Konfiguration

Die Einstellungen werden in `~/.config/pibox5/settings.yaml` gespeichert.

### Wichtige Einstellungen

| Einstellung | Beschreibung | Standard |
|-------------|--------------|----------|
| `countdown_seconds` | Countdown-Dauer | 3 |
| `review_seconds` | Review-Anzeige-Dauer | 5 |
| `theme` | UI-Theme (default/dark) | default |
| `upload_url` | REST-API Endpoint | - |
| `upload_api_key` | API-Authentifizierung | - |

## Kamera-Einstellungen

Unterstützte Kamera-Parameter (via gPhoto2):
- ISO (Auto, 100-1600)
- Blende (abhängig vom Objektiv)
- Verschlusszeit
- Bildqualität

## Projekt-Struktur

```
pibox5/
├── camera/          # Kamera-Abstraktionsschicht
├── config/          # Settings & Konfiguration
├── ui/
│   ├── screens/     # Idle, Countdown, Review, Settings
│   ├── widgets/     # Wiederverwendbare UI-Komponenten
│   └── themes/      # QSS Stylesheets
└── upload/          # REST-API Upload
```

## Entwicklung

```bash
# Dev-Dependencies installieren
pip install -e ".[dev]"

# Tests ausführen
pytest

# Code formatieren
black pibox5/
ruff check pibox5/
```

## Lizenz

MIT License - siehe [LICENSE](LICENSE)

## Danksagung

- [gPhoto2](http://gphoto.org/) - Kamera-Steuerung
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI Framework
- Die Raspberry Pi Foundation
