"""
HTTP Upload module for REST API photo uploads.

Provides async upload with retry logic and queue management.
"""

import threading
import queue
import time
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import requests


@dataclass
class UploadTask:
    """Represents a photo upload task."""
    
    image_data: bytes
    filename: str
    timestamp: datetime
    retry_count: int = 0


@dataclass
class UploadResult:
    """Result of an upload operation."""
    
    success: bool
    filename: str
    status_code: Optional[int] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    upload_time_ms: int = 0


class HttpUploader:
    """
    HTTP uploader with background thread and retry logic.
    
    Features:
    - Async upload via background thread
    - Automatic retry on failure
    - Queue for offline buffering
    - Configurable timeout and headers
    """
    
    def __init__(
        self,
        url: str,
        api_key: str = "",
        timeout: int = 30,
        retry_count: int = 3,
        retry_delay: float = 2.0,
        on_success: Optional[Callable[[UploadResult], None]] = None,
        on_error: Optional[Callable[[UploadResult], None]] = None,
    ):
        """
        Initialize the HTTP uploader.
        
        Args:
            url: REST API endpoint URL.
            api_key: API key for authentication (sent as X-API-Key header).
            timeout: Request timeout in seconds.
            retry_count: Number of retry attempts.
            retry_delay: Delay between retries in seconds.
            on_success: Callback for successful uploads.
            on_error: Callback for failed uploads.
        """
        self.url = url
        self.api_key = api_key
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.on_success = on_success
        self.on_error = on_error
        
        # Upload queue and worker thread
        self._queue: queue.Queue[UploadTask] = queue.Queue()
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        
        # Statistics
        self._total_uploads = 0
        self._successful_uploads = 0
        self._failed_uploads = 0
        
        # Start worker thread
        self._start_worker()
    
    def _start_worker(self):
        """Start the background worker thread."""
        if self._worker_thread is not None and self._worker_thread.is_alive():
            return
        
        self._running = True
        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            daemon=True,
            name="UploadWorker",
        )
        self._worker_thread.start()
        print("[HttpUploader] Worker thread started")
    
    def _worker_loop(self):
        """Background worker loop."""
        while self._running:
            try:
                # Get task with timeout to allow periodic checks
                task = self._queue.get(timeout=1.0)
                
                # Process upload
                result = self._upload_with_retry(task)
                
                # Call appropriate callback
                if result.success:
                    self._successful_uploads += 1
                    if self.on_success:
                        self.on_success(result)
                else:
                    self._failed_uploads += 1
                    if self.on_error:
                        self.on_error(result)
                
                self._queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[HttpUploader] Worker error: {e}")
    
    def _upload_with_retry(self, task: UploadTask) -> UploadResult:
        """
        Upload with retry logic.
        
        Args:
            task: Upload task to process.
            
        Returns:
            UploadResult with status.
        """
        last_error = None
        
        for attempt in range(self.retry_count + 1):
            try:
                result = self._do_upload(task)
                if result.success:
                    return result
                last_error = result.error_message
                
            except Exception as e:
                last_error = str(e)
            
            # Wait before retry (except on last attempt)
            if attempt < self.retry_count:
                print(f"[HttpUploader] Retry {attempt + 1}/{self.retry_count} for {task.filename}")
                time.sleep(self.retry_delay)
        
        # All retries failed
        return UploadResult(
            success=False,
            filename=task.filename,
            error_message=f"Upload failed after {self.retry_count + 1} attempts: {last_error}",
        )
    
    def _do_upload(self, task: UploadTask) -> UploadResult:
        """
        Perform the actual HTTP upload.
        
        Args:
            task: Upload task.
            
        Returns:
            UploadResult.
        """
        start_time = time.time()
        
        # Prepare headers
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        # Prepare multipart form data
        files = {
            "photo": (task.filename, task.image_data, "image/jpeg"),
        }
        
        # Additional form data
        data = {
            "timestamp": task.timestamp.isoformat(),
            "source": "pibox5",
        }
        
        try:
            # Make request
            response = requests.post(
                self.url,
                files=files,
                data=data,
                headers=headers,
                timeout=self.timeout,
            )
            
            upload_time = int((time.time() - start_time) * 1000)
            
            # Check response
            if response.ok:
                print(f"[HttpUploader] Upload successful: {task.filename} ({upload_time}ms)")
                
                # Try to parse JSON response
                try:
                    response_data = response.json()
                except ValueError:
                    response_data = {"raw": response.text[:200]}
                
                return UploadResult(
                    success=True,
                    filename=task.filename,
                    status_code=response.status_code,
                    response_data=response_data,
                    upload_time_ms=upload_time,
                )
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                print(f"[HttpUploader] Upload failed: {error_msg}")
                
                return UploadResult(
                    success=False,
                    filename=task.filename,
                    status_code=response.status_code,
                    error_message=error_msg,
                    upload_time_ms=upload_time,
                )
                
        except requests.Timeout:
            return UploadResult(
                success=False,
                filename=task.filename,
                error_message=f"Request timeout after {self.timeout}s",
            )
        except requests.ConnectionError as e:
            return UploadResult(
                success=False,
                filename=task.filename,
                error_message=f"Connection error: {e}",
            )
        except Exception as e:
            return UploadResult(
                success=False,
                filename=task.filename,
                error_message=f"Upload error: {e}",
            )
    
    def upload_async(self, image_data: bytes, filename: str):
        """
        Queue a photo for async upload.
        
        Args:
            image_data: JPEG image bytes.
            filename: Filename for the upload.
        """
        self._total_uploads += 1
        
        task = UploadTask(
            image_data=image_data,
            filename=filename,
            timestamp=datetime.now(),
        )
        
        self._queue.put(task)
        print(f"[HttpUploader] Queued: {filename} (queue size: {self._queue.qsize()})")
    
    def upload_sync(self, image_data: bytes, filename: str) -> UploadResult:
        """
        Upload a photo synchronously (blocking).
        
        Args:
            image_data: JPEG image bytes.
            filename: Filename for the upload.
            
        Returns:
            UploadResult.
        """
        self._total_uploads += 1
        
        task = UploadTask(
            image_data=image_data,
            filename=filename,
            timestamp=datetime.now(),
        )
        
        result = self._upload_with_retry(task)
        
        if result.success:
            self._successful_uploads += 1
        else:
            self._failed_uploads += 1
        
        return result
    
    def get_stats(self) -> Dict[str, int]:
        """Get upload statistics."""
        return {
            "total": self._total_uploads,
            "successful": self._successful_uploads,
            "failed": self._failed_uploads,
            "pending": self._queue.qsize(),
        }
    
    def get_queue_size(self) -> int:
        """Get number of pending uploads."""
        return self._queue.qsize()
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown the uploader.
        
        Args:
            wait: Whether to wait for pending uploads to complete.
        """
        print("[HttpUploader] Shutting down...")
        
        if wait:
            # Wait for queue to empty
            self._queue.join()
        
        self._running = False
        
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)
        
        print("[HttpUploader] Shutdown complete")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown(wait=True)
        return False
