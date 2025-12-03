# Plan: PiBox5 Backend mit PHP

Ein einfaches PHP-Backend für Foto-Uploads mit API-Key-Authentifizierung und Web-Galerie, gehostet unter `pibox5.neuhauser.cloud`.

## Projektstruktur

```
backend/
├── .htaccess             # URL-Rewriting, Sicherheit
├── config.php            # API-Key und Einstellungen
├── upload.php            # Upload-Endpoint (POST)
├── gallery.php           # Web-Galerie (HTML)
├── api/
│   └── photos.php        # JSON-API für Foto-Liste
└── uploads/              # Gespeicherte Fotos
    └── .htaccess         # Direktzugriff erlauben
```

## Steps

1. **Erstelle `config.php`** mit:
   - `API_KEY`: Einziger erlaubter API-Key
   - `UPLOAD_DIR`: Pfad zum Upload-Ordner
   - `MAX_FILE_SIZE`: Maximale Dateigröße (z.B. 10MB)
   - `ALLOWED_TYPES`: Erlaubte MIME-Types (image/jpeg)

2. **Erstelle `upload.php`** mit:
   - Prüft `X-API-Key` Header gegen `API_KEY`
   - Empfängt `multipart/form-data` mit `photo` Feld
   - Validiert Dateityp und -größe
   - Speichert mit Zeitstempel-Dateiname
   - Gibt JSON-Response zurück

3. **Erstelle `gallery.php`** mit:
   - Responsive HTML/CSS Galerie
   - Thumbnail-Grid aller Fotos
   - Lightbox für Vollbild-Ansicht
   - Sortierung nach Datum (neueste zuerst)
   - Download-Button

4. **Erstelle `.htaccess`** mit:
   - RewriteRule für saubere URLs
   - Sicherheits-Header
   - PHP-Einstellungen (upload_max_filesize)

5. **Deployment** auf `pibox5.neuhauser.cloud`:
   - Dateien per FTP/SSH hochladen
   - Upload-Ordner erstellen mit Schreibrechten (chmod 755)
   - API-Key in config.php setzen

## Technologie-Stack

- **PHP 8.x** - Serverseitige Logik
- **HTML5/CSS3** - Galerie-Frontend
- **Vanilla JS** - Lightbox-Funktionalität
- **Lokaler Storage** - Fotos im `uploads/` Ordner
