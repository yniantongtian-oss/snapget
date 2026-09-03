import os
import re
import urllib.request
import urllib.error
from pathlib import Path
from typing import Callable, Optional
from .models import MediaItem, ParseResult


def sanitize_filename(filename: str, max_length: int = 120) -> str:
    """Sanitizes filename for Windows/Linux/macOS filesystems."""
    # Replace illegal characters with underscore
    cleaned = re.sub(r'[\\/*?:"<>|\r\n\t]', "_", filename)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        cleaned = "downloaded_media"
    return cleaned[:max_length]


class MediaDownloader:
    """Robust multi-threaded / streaming chunked downloader with header support."""

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        )
    }

    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_item(
        self,
        item: MediaItem,
        folder_name: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Path:
        """
        Downloads a single MediaItem to the target directory.
        progress_callback: receives (downloaded_bytes, total_bytes)
        """
        target_dir = self.output_dir
        if folder_name:
            target_dir = target_dir / sanitize_filename(folder_name)
            target_dir.mkdir(parents=True, exist_ok=True)

        clean_name = sanitize_filename(item.filename)
        dest_path = target_dir / clean_name

        req_headers = {**self.DEFAULT_HEADERS, **item.headers}
        req = urllib.request.Request(item.url, headers=req_headers)

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 64 * 1024  # 64 KB

                with open(dest_path, "wb") as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)

        except Exception as e:
            if dest_path.exists() and dest_path.stat().st_size == 0:
                dest_path.unlink()
            raise RuntimeError(f"Download failed for {item.url}: {e}") from e

        return dest_path

    def download_all(
        self,
        result: ParseResult,
        item_callback: Optional[Callable[[MediaItem, Path], None]] = None,
    ) -> list[Path]:
        """Downloads all media items within a ParseResult into a subfolder named after the title."""
        folder_name = f"{result.platform}_{result.title}" if result.title else result.platform
        downloaded_paths = []
        for item in result.items:
            path = self.download_item(item, folder_name=folder_name)
            downloaded_paths.append(path)
            if item_callback:
                item_callback(item, path)
        return downloaded_paths
