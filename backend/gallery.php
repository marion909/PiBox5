<?php
/**
 * PiBox5 Photo Gallery
 * 
 * Responsive Web-Galerie mit Lightbox für alle hochgeladenen Fotos.
 */

require_once __DIR__ . '/config.php';

// Fotos aus Upload-Verzeichnis laden
$photos = [];
if (is_dir(UPLOAD_DIR)) {
    $files = glob(UPLOAD_DIR . '*.{jpg,jpeg,JPG,JPEG}', GLOB_BRACE);
    foreach ($files as $file) {
        $photos[] = [
            'filename' => basename($file),
            'path' => 'uploads/' . basename($file),
            'size' => filesize($file),
            'date' => filemtime($file)
        ];
    }
    // Nach Datum sortieren (neueste zuerst)
    usort($photos, fn($a, $b) => $b['date'] - $a['date']);
}

$photoCount = count($photos);
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars(SITE_TITLE) ?></title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        
        header {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid rgba(233, 69, 96, 0.3);
        }
        
        h1 {
            font-size: 2rem;
            margin-bottom: 8px;
            background: linear-gradient(90deg, #ff6b6b, #e94560);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .photo-count {
            color: rgba(255, 255, 255, 0.7);
            font-size: 1rem;
        }
        
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .photo-card {
            position: relative;
            aspect-ratio: 4/3;
            overflow: hidden;
            border-radius: 12px;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            background: rgba(0, 0, 0, 0.3);
        }
        
        .photo-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(233, 69, 96, 0.3);
        }
        
        .photo-card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }
        
        .photo-card:hover img {
            transform: scale(1.05);
        }
        
        .photo-info {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 10px;
            background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.8);
        }
        
        /* Lightbox */
        .lightbox {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        
        .lightbox.active {
            display: flex;
        }
        
        .lightbox img {
            max-width: 90%;
            max-height: 80%;
            object-fit: contain;
            border-radius: 8px;
        }
        
        .lightbox-controls {
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 15px;
        }
        
        .lightbox-btn {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.5rem;
            transition: background 0.3s;
        }
        
        .lightbox-btn:hover {
            background: rgba(233, 69, 96, 0.5);
        }
        
        .lightbox-nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 2rem;
            transition: background 0.3s;
        }
        
        .lightbox-nav:hover {
            background: rgba(233, 69, 96, 0.5);
        }
        
        .lightbox-nav.prev {
            left: 20px;
        }
        
        .lightbox-nav.next {
            right: 20px;
        }
        
        .lightbox-info {
            margin-top: 15px;
            color: rgba(255, 255, 255, 0.7);
            text-align: center;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: rgba(255, 255, 255, 0.6);
        }
        
        .empty-state svg {
            width: 80px;
            height: 80px;
            margin-bottom: 20px;
            opacity: 0.5;
        }
        
        @media (max-width: 600px) {
            .gallery {
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
                padding: 10px;
            }
            
            h1 {
                font-size: 1.5rem;
            }
            
            .lightbox-nav {
                width: 45px;
                height: 45px;
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>📸 <?= htmlspecialchars(SITE_TITLE) ?></h1>
        <p class="photo-count"><?= $photoCount ?> Foto<?= $photoCount !== 1 ? 's' : '' ?></p>
    </header>
    
    <?php if ($photoCount > 0): ?>
    <div class="gallery">
        <?php foreach ($photos as $index => $photo): ?>
        <div class="photo-card" data-index="<?= $index ?>" onclick="openLightbox(<?= $index ?>)">
            <img src="<?= htmlspecialchars($photo['path']) ?>" 
                 alt="Foto vom <?= date('d.m.Y H:i', $photo['date']) ?>"
                 loading="lazy">
            <div class="photo-info">
                <?= date('d.m.Y H:i', $photo['date']) ?>
            </div>
        </div>
        <?php endforeach; ?>
    </div>
    
    <!-- Lightbox -->
    <div class="lightbox" id="lightbox">
        <div class="lightbox-controls">
            <a class="lightbox-btn" id="downloadBtn" href="#" download title="Download">⬇</a>
            <button class="lightbox-btn" onclick="closeLightbox()" title="Schließen">✕</button>
        </div>
        <button class="lightbox-nav prev" onclick="navigateLightbox(-1)">‹</button>
        <img id="lightboxImg" src="" alt="">
        <button class="lightbox-nav next" onclick="navigateLightbox(1)">›</button>
        <div class="lightbox-info" id="lightboxInfo"></div>
    </div>
    
    <script>
        const photos = <?= json_encode($photos) ?>;
        let currentIndex = 0;
        
        function openLightbox(index) {
            currentIndex = index;
            updateLightbox();
            document.getElementById('lightbox').classList.add('active');
            document.body.style.overflow = 'hidden';
        }
        
        function closeLightbox() {
            document.getElementById('lightbox').classList.remove('active');
            document.body.style.overflow = '';
        }
        
        function navigateLightbox(direction) {
            currentIndex = (currentIndex + direction + photos.length) % photos.length;
            updateLightbox();
        }
        
        function updateLightbox() {
            const photo = photos[currentIndex];
            document.getElementById('lightboxImg').src = photo.path;
            document.getElementById('downloadBtn').href = photo.path;
            document.getElementById('lightboxInfo').textContent = 
                `${currentIndex + 1} / ${photos.length} — ${new Date(photo.date * 1000).toLocaleString('de-DE')}`;
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (!document.getElementById('lightbox').classList.contains('active')) return;
            
            if (e.key === 'Escape') closeLightbox();
            if (e.key === 'ArrowLeft') navigateLightbox(-1);
            if (e.key === 'ArrowRight') navigateLightbox(1);
        });
        
        // Close on background click
        document.getElementById('lightbox').addEventListener('click', (e) => {
            if (e.target.id === 'lightbox') closeLightbox();
        });
    </script>
    
    <?php else: ?>
    <div class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
                  d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
                  d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        <h2>Noch keine Fotos</h2>
        <p>Fotos werden hier erscheinen, sobald sie hochgeladen wurden.</p>
    </div>
    <?php endif; ?>
</body>
</html>
