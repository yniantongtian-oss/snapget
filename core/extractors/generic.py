import re
from .base import BaseExtractor
from ..models import ParseResult, MediaItem, MediaType

try:
    import yt_dlp
    HAS_YTDLP = True
except ImportError:
    HAS_YTDLP = False


class GenericExtractor(BaseExtractor):
    """Fallback extractor using yt-dlp for wider platform coverage (YouTube, Weibo, X, etc.)"""

    PLATFORM_NAME = "generic"
    URL_PATTERNS = [re.compile(r"^https?://", re.IGNORECASE)]

    def parse(self, raw_text_or_url: str) -> ParseResult:
        clean_url = self.extract_url_from_text(raw_text_or_url) or raw_text_or_url
        if not HAS_YTDLP:
            raise NotImplementedError(
                "Generic fallback extractor requires yt-dlp to be installed."
            )

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)

        title = info.get("title", "generic_media")
        author = info.get("uploader", "author")
        extractor_key = info.get("extractor_key", "generic").lower()
        cover_url = info.get("thumbnail")

        # Extract best direct URL
        video_url = info.get("url")
        if not video_url and "formats" in info:
            # Pick highest quality format with direct url
            formats = [f for f in info["formats"] if f.get("url")]
            if formats:
                video_url = formats[-1]["url"]

        if not video_url:
            raise RuntimeError(f"Unable to extract streaming URL via generic extractor for {clean_url}")

        items = [
            MediaItem(
                url=video_url,
                media_type=MediaType.VIDEO,
                title=title,
                filename=f"{author}_{title[:30]}.mp4",
                headers=info.get("http_headers", {}),
            )
        ]

        return ParseResult(
            platform=extractor_key,
            title=title,
            author=author,
            media_type=MediaType.VIDEO,
            items=items,
            cover_url=cover_url,
            raw_url=clean_url,
            description=info.get("description", ""),
        )
