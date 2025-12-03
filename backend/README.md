# PiBox5 Backend

PHP-Backend für die PiBox5 Fotobox mit Web-Galerie.

## Dateien

| Datei | Beschreibung |
|-------|-------------|
| `config.php` | Konfiguration (API-Key, Pfade) |
| `upload.php` | Upload-Endpoint für Fotos |
| `gallery.php` | Web-Galerie mit Lightbox |
| `api/photos.php` | JSON-API für Foto-Liste |

## Installation

1. Dateien auf Webserver hochladen (z.B. `pibox5.neuhauser.cloud`)
2. `config.php` bearbeiten und `API_KEY` setzen
3. Upload-Ordner erstellen: `mkdir uploads && chmod 755 uploads`

## API-Nutzung

### Foto hochladen

```bash
curl -X POST https://pibox5.neuhauser.cloud/upload.php \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "photo=@foto.jpg"
```

**Response:**
```json
{
  "success": true,
  "filename": "photo_2025-12-03_14-30-00_abc123.jpg",
  "size": 1234567,
  "url": "uploads/photo_2025-12-03_14-30-00_abc123.jpg"
}
```

### Foto-Liste abrufen

```bash
curl https://pibox5.neuhauser.cloud/api/photos.php
```

## Galerie

Die Galerie ist unter der Root-URL erreichbar:
- `https://pibox5.neuhauser.cloud/` → Galerie
- `https://pibox5.neuhauser.cloud/gallery.php` → Galerie

### Features

- Responsive Grid-Layout
- Lightbox mit Tastatur-Navigation (←/→/Esc)
- Download-Button
- Sortierung nach Datum (neueste zuerst)

## Sicherheit

- API-Key-Authentifizierung für Uploads
- MIME-Type-Validierung (nur JPEG)
- Dateigrößen-Limit (10 MB)
- PHP-Ausführung im Upload-Ordner blockiert
- Config-Datei nicht von außen zugänglich
