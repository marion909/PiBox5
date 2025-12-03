# PiBox5 - Modern Photo Booth for Raspberry Pi 5

Eine elegante Fotobox-Anwendung für Raspberry Pi 5 mit Canon DSLR-Unterstützung und Web-Galerie.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green.svg)
![PHP](https://img.shields.io/badge/PHP-8.x-777BB4.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

### Fotobox (Raspberry Pi)
- 🎥 **Live-Vorschau** mit Blur-Effekt im Idle-Modus
- 📸 **Countdown-Timer** (konfigurierbar 1-10 Sekunden)
- 🖼️ **Review-Screen** mit automatischem Timeout
- ⚙️ **Touch-freundliches Settings-Menü** (optimiert für 800x480)
- 📤 **Automatischer Upload** zum Backend-Server
- 🎨 **Theme-System** mit hellen und dunklen Themes
- 📷 **Canon EOS Unterstützung** via gPhoto2

### Backend (Web-Server)
- ☁️ **REST-API** für Foto-Uploads mit API-Key Auth
- 🖼️ **Web-Galerie** mit Lightbox und Download
- 📱 **Responsive Design** für alle Geräte

## Hardware-Anforderungen

- Raspberry Pi 5 (4GB+ RAM empfohlen)
- 7" OSOYOO DSI Touch Display (800x480)
- Canon EOS 1000D (oder andere gPhoto2-kompatible Kamera)
- USB-Kabel für Kamera

## Quick Install (Raspberry Pi)

```bash
# Repository klonen
git clone https://github.com/marion909/PiBox5.git
cd PiBox5

# Installation starten
./scripts/install.sh

# Starten
pibox5 --dummy-camera  # Test-Modus
pibox5                  # Mit Kamera
```

## Manuelle Installation

### 1. System-Dependencies

```bash
sudo apt update
sudo apt install -y \
    python3-pip python3-venv \
    gphoto2 libgphoto2-dev \
    libgl1 libegl1 libgles2 \
    libxcb-xinerama0 libxcb-cursor0
```

### 2. Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Starten

```bash
# Mit echter Kamera
pibox5

# Ohne Kamera (Demo-Modus)
pibox5 --dummy-camera

# Beenden: Escape oder Ctrl+C
```

## Backend-Installation (Web-Server)

Das Backend läuft auf einem beliebigen PHP-Webserver (z.B. Apache, nginx).

### 1. Dateien hochladen

```bash
# Backend-Ordner auf Server kopieren
scp -r backend/* user@pibox5.neuhauser.cloud:/var/www/html/
```

### 2. Konfiguration

In `config.php` den API-Key setzen:
```php
define('API_KEY', 'DEIN_SICHERER_API_KEY');
```

### 3. Rechte setzen

```bash
chmod 755 uploads/
```

### 4. Galerie aufrufen

```
https://pibox5.neuhauser.cloud/
```

## Konfiguration

Die Einstellungen werden in `~/.config/pibox5/settings.yaml` gespeichert.

### Fotobox-Einstellungen

| Einstellung | Beschreibung | Standard |
|-------------|--------------|----------|
| `countdown_seconds` | Countdown-Dauer | 3 |
| `review_seconds` | Review-Anzeige-Dauer | 5 |
| `button_size` | Foto-Button Größe | 120 |
| `theme` | UI-Theme (default/dark) | default |

### Upload-Einstellungen

| Einstellung | Beschreibung | Standard |
|-------------|--------------|----------|
| `upload.enabled` | Upload aktivieren | false |
| `upload.url` | Backend-URL | - |
| `upload.api_key` | API-Schlüssel | - |
| `upload.upload_on_capture` | Auto-Upload | true |

## Projekt-Struktur

```
PiBox5/
├── pibox5/              # Python Fotobox-App
│   ├── camera/          # Kamera-Abstraktionsschicht
│   ├── config/          # Settings & Konfiguration
│   ├── ui/
│   │   ├── screens/     # Idle, Countdown, Review, Settings
│   │   ├── widgets/     # UI-Komponenten
│   │   └── themes/      # QSS Stylesheets
│   └── upload/          # HTTP Upload-Client
├── backend/             # PHP Backend
│   ├── config.php       # API-Key Konfiguration
│   ├── upload.php       # Upload-Endpoint
│   ├── gallery.php      # Web-Galerie
│   ├── api/photos.php   # JSON-API
│   └── uploads/         # Foto-Speicher
└── scripts/
    └── install.sh       # Installations-Script
```

## API-Dokumentation

### Foto hochladen

```bash
curl -X POST https://pibox5.neuhauser.cloud/upload.php \
  -H "X-API-Key: DEIN_API_KEY" \
  -F "photo=@foto.jpg"
```

**Response:**
```json
{
  "success": true,
  "filename": "photo_2025-12-03_14-30-00_abc123.jpg",
  "url": "uploads/photo_2025-12-03_14-30-00_abc123.jpg"
}
```

### Foto-Liste abrufen

```bash
curl https://pibox5.neuhauser.cloud/api/photos.php
```

## Lizenz

MIT License - siehe [LICENSE](LICENSE)

## Danksagung

- [gPhoto2](http://gphoto.org/) - Kamera-Steuerung
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI Framework
- Die Raspberry Pi Foundation
