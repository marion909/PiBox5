<?php
/**
 * PiBox5 Upload Endpoint
 * 
 * Empfängt Fotos von der Fotobox und speichert sie lokal.
 * Erwartet multipart/form-data mit:
 * - photo: JPEG-Datei
 * - timestamp: ISO-Zeitstempel (optional)
 * - source: Quell-Identifier (optional)
 * 
 * Header:
 * - X-API-Key: API-Schlüssel zur Authentifizierung
 */

require_once __DIR__ . '/config.php';

// CORS Headers
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: X-API-Key, Content-Type');
header('Content-Type: application/json; charset=utf-8');

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Nur POST erlauben
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode([
        'success' => false,
        'error' => 'Method not allowed. Use POST.'
    ]);
    exit;
}

// API-Key prüfen
$apiKey = $_SERVER['HTTP_X_API_KEY'] ?? '';
if ($apiKey !== API_KEY) {
    http_response_code(401);
    echo json_encode([
        'success' => false,
        'error' => 'Invalid or missing API key'
    ]);
    exit;
}

// Prüfen ob Datei hochgeladen wurde
if (!isset($_FILES['photo']) || $_FILES['photo']['error'] !== UPLOAD_ERR_OK) {
    $errorMessages = [
        UPLOAD_ERR_INI_SIZE => 'File exceeds upload_max_filesize',
        UPLOAD_ERR_FORM_SIZE => 'File exceeds MAX_FILE_SIZE',
        UPLOAD_ERR_PARTIAL => 'File was only partially uploaded',
        UPLOAD_ERR_NO_FILE => 'No file was uploaded',
        UPLOAD_ERR_NO_TMP_DIR => 'Missing temporary folder',
        UPLOAD_ERR_CANT_WRITE => 'Failed to write file to disk',
    ];
    
    $errorCode = $_FILES['photo']['error'] ?? UPLOAD_ERR_NO_FILE;
    $errorMsg = $errorMessages[$errorCode] ?? 'Unknown upload error';
    
    http_response_code(400);
    echo json_encode([
        'success' => false,
        'error' => $errorMsg
    ]);
    exit;
}

$file = $_FILES['photo'];

// Dateigröße prüfen
if ($file['size'] > MAX_FILE_SIZE) {
    http_response_code(413);
    echo json_encode([
        'success' => false,
        'error' => 'File too large. Maximum size: ' . (MAX_FILE_SIZE / 1024 / 1024) . ' MB'
    ]);
    exit;
}

// MIME-Type prüfen
$finfo = new finfo(FILEINFO_MIME_TYPE);
$mimeType = $finfo->file($file['tmp_name']);

if (!in_array($mimeType, ALLOWED_TYPES)) {
    http_response_code(415);
    echo json_encode([
        'success' => false,
        'error' => 'Invalid file type. Only JPEG allowed.'
    ]);
    exit;
}

// Upload-Verzeichnis erstellen falls nicht vorhanden
if (!is_dir(UPLOAD_DIR)) {
    if (!mkdir(UPLOAD_DIR, 0755, true)) {
        http_response_code(500);
        echo json_encode([
            'success' => false,
            'error' => 'Failed to create upload directory'
        ]);
        exit;
    }
}

// Eindeutigen Dateinamen generieren
$timestamp = $_POST['timestamp'] ?? date('c');
$datePrefix = date('Y-m-d_H-i-s');
$uniqueId = substr(uniqid(), -6);
$filename = "photo_{$datePrefix}_{$uniqueId}.jpg";
$filepath = UPLOAD_DIR . $filename;

// Datei speichern
if (!move_uploaded_file($file['tmp_name'], $filepath)) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Failed to save file'
    ]);
    exit;
}

// Erfolg
http_response_code(201);
echo json_encode([
    'success' => true,
    'filename' => $filename,
    'size' => $file['size'],
    'timestamp' => $timestamp,
    'url' => 'uploads/' . $filename
]);
