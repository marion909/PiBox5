<?php
/**
 * PiBox5 Backend Configuration
 * 
 * WICHTIG: API_KEY vor Deployment ändern!
 */

// API-Key für Authentifizierung
define('API_KEY', 'CHANGE_ME_TO_SECURE_KEY_123');

// Upload-Einstellungen
define('UPLOAD_DIR', __DIR__ . '/uploads/');
define('MAX_FILE_SIZE', 10 * 1024 * 1024); // 10 MB
define('ALLOWED_TYPES', ['image/jpeg', 'image/jpg']);

// Galerie-Einstellungen
define('PHOTOS_PER_PAGE', 50);
define('SITE_TITLE', 'PiBox5 Fotogalerie');

// Thumbnail-Einstellungen (optional für spätere Erweiterung)
define('THUMBNAIL_SIZE', 300);

// Timezone
date_default_timezone_set('Europe/Berlin');

// Error Reporting (in Produktion ausschalten)
// error_reporting(E_ALL);
// ini_set('display_errors', 1);
