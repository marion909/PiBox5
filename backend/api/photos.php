<?php
/**
 * PiBox5 Photos API
 * 
 * JSON-API zum Abrufen der Foto-Liste.
 * Optional mit API-Key geschützt.
 */

require_once __DIR__ . '/../config.php';

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

// Fotos aus Upload-Verzeichnis laden
$photos = [];
if (is_dir(UPLOAD_DIR)) {
    $files = glob(UPLOAD_DIR . '*.{jpg,jpeg,JPG,JPEG}', GLOB_BRACE);
    foreach ($files as $file) {
        $photos[] = [
            'filename' => basename($file),
            'url' => 'uploads/' . basename($file),
            'size' => filesize($file),
            'date' => date('c', filemtime($file))
        ];
    }
    // Nach Datum sortieren (neueste zuerst)
    usort($photos, fn($a, $b) => strtotime($b['date']) - strtotime($a['date']));
}

echo json_encode([
    'success' => true,
    'count' => count($photos),
    'photos' => $photos
], JSON_PRETTY_PRINT);
