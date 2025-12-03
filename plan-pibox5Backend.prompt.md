# Plan: PiBox5 Backend mit API-Key Auth

Ein FastAPI-Backend für Foto-Uploads, gehostet unter `pibox5.neuhauser.cloud`.

## Projektstruktur

```
backend/
├── requirements.txt       # FastAPI, uvicorn, python-multipart
├── .env.example          # Template für Umgebungsvariablen
├── config.py             # Settings mit Pydantic
├── main.py               # FastAPI App
├── auth.py               # API-Key Validierung
├── models.py             # Pydantic Models
└── uploads/              # Gespeicherte Fotos
```

## Steps

1. **Erstelle `backend/requirements.txt`** mit FastAPI, uvicorn, python-multipart, Pillow, aiofiles

2. **Erstelle `backend/config.py`** mit Pydantic Settings für:
   - `API_KEYS`: Liste erlaubter API-Keys
   - `UPLOAD_DIR`: Speicherort für Fotos
   - `MAX_FILE_SIZE`: Maximale Dateigröße

3. **Erstelle `backend/auth.py`** mit:
   - `verify_api_key()` Dependency für FastAPI
   - Prüft `X-API-Key` Header gegen erlaubte Keys

4. **Erstelle `backend/main.py`** mit:
   - `POST /upload` - Foto empfangen und speichern
   - `GET /photos` - Liste aller Fotos (optional)
   - `GET /health` - Health-Check Endpoint
   - CORS für Frontend-Zugriff

5. **Deployment-Config** für `pibox5.neuhauser.cloud`:
   - Systemd Service oder Docker
   - Nginx Reverse Proxy mit SSL

## Weitere Überlegungen

1. **API-Key Management**: Sollen mehrere Keys erlaubt sein? (z.B. pro Fotobox)
2. **Speicher**: Lokaler Ordner oder Cloud-Storage (S3)?
3. **Galerie**: Soll eine Web-Galerie zum Ansehen der Fotos erstellt werden?
